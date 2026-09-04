#!/usr/bin/env bash
# Session keepalive + coordination heartbeat that MEASURES rather than repeats.
#
# ── THREE FAILURE MODES, ALL HIT FOR REAL, ALL FIXED HERE ──────────────────────────────────────────────
# 1. SNAPSHOT (silent_nulls 32): a first version read the file once at startup and rewrote that copy every
#    tick, silently reverting ten hours of updates. Fix: re-read every tick, never cache.
# 2. TIMESTAMP-ONLY (TheBridge, 2026-08-22): bumping `updated` while leaving every other field alone produces
#    a file whose clock is always fresh and whose CONTENT is arbitrarily old. This is worse than a frozen
#    file, because a frozen file is DETECTABLE -- `updated` stops and stale_after_s fires -- whereas a
#    clock driven independently of content is undetectable by construction: it emits the exact signature the
#    staleness check was built to certify as healthy.
#       >> NEVER UPDATE `updated` ON ITS OWN. That field is a claim about all the others. <<
# 3. SELF-COUNTING: `pgrep -f SpaceTime/curvature` matched THIS SCRIPT, so the liveness probe counted the
#    monitor as evidence of activity. A monitor must exclude itself or it always reports life.
# 4. ARGV-AS-IDENTITY (silent_nulls 46/49): that same pgrep could not see a job launched by RELATIVE path, and
#    the usual `| grep -v grep` hygiene deletes any neighbour that is itself a grep. Both directions produce
#    the identical output -- an empty scan -- whether the machine is idle or busy. Now enumerated by CWD.
#
# ── THE STRUCTURAL FIX: separate DECLARED from DERIVED ─────────────────────────────────────────────────
# `state`/`detail` are DECLARED -- a human/agent types them and they are stale the moment work moves on. No
# heartbeat can refresh a declaration. So they are marked as declarations, carry their own age, and are never
# what a reader should schedule against. `measured` is DERIVED from the machine every tick; it cannot be
# faked by a loop that does not actually look, and its numbers JITTER, which is what distinguishes a real
# heartbeat from a bumping one.
set -eu
S=/Users/sumit/Github/.claude-coordination/tabula.status
LOG=/Users/sumit/Github/.claude-coordination/tabula.keepalive.log

# LOG WHY IT DIES. This loop has been killed several times (exit 143, 144) and each death told us nothing,
# because the script only printed on NORMAL completion. Streams were captured -- unlike a /dev/null detach --
# but nothing was ever emitted on an abnormal exit, so the channel existed and carried nothing. That LOOKS
# instrumented, which is worse than obviously not being. (TheBridge hit the /dev/null version of this three
# times while telling everyone to run things rather than read them.)
_bye() { c=$?; echo "$(date -u +%FT%TZ) keepalive pid $$ EXIT code=$c signal_ctx=${1:-none}" >> "$LOG"; }
trap '_bye EXIT'  EXIT
trap '_bye TERM; exit 143' TERM
trap '_bye INT;  exit 130' INT
trap '_bye HUP;  exit 129' HUP
echo "$(date -u +%FT%TZ) keepalive pid $$ START" >> "$LOG"
# LINEAGE, captured now and not later: once this process is disowned its ppid becomes 1 and the chain to the
# launching shell is gone. Needed because cwd-based enumeration correctly finds OUR OWN shell and harness
# sitting in the repo, and counting those as activity is failure mode 3 wearing a new costume. Excluding by
# lineage is computed and exact; excluding by name ("zsh", "sleep") would repeat silent_nulls 49 from the
# other side -- deleting a neighbour for resembling us.
ANCESTORS="$$"; _a=$$
for _ in 1 2 3 4 5 6 7 8; do
  _a=$(ps -o ppid= -p "$_a" 2>/dev/null | tr -d ' ')
  [ -z "$_a" ] || [ "$_a" = "0" ] || [ "$_a" = "1" ] && break
  ANCESTORS="$ANCESTORS,$_a"
done
export ANCESTORS
HOURS="${1:-10}"
END=$(( $(date +%s) + HOURS * 3600 ))
SELF=$$
while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$S" ]; then
    python3 - "$S" "$SELF" "$ANCESTORS" << 'PY' 2>/dev/null || true
import json, os, subprocess, sys, datetime
p, self_pid = sys.argv[1], int(sys.argv[2])
ancestors = {int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "").split(",") if x.strip().isdigit()}
try:
    d = json.load(open(p))                       # re-read every tick: no snapshot, ever
except Exception:
    sys.exit(0)
now = datetime.datetime.now(datetime.timezone.utc)

def sh(c):
    try: return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=8).stdout
    except Exception: return ""

# --- DERIVED: measured fresh every tick, excluding this script and its children ---
# 4. ARGV IS NOT AN IDENTIFIER (silent_nulls 46/49). The previous scan matched `pgrep -f SpaceTime/curvature`,
#    i.e. against argv -- a string the LAUNCHER chose. A job started as `./curvature/scripts/foo.py` carries no
#    absolute path, so it was INVISIBLE here and this file would publish a measured, jittering `n_procs: 0`
#    while the machine computed. Verified live on a sibling's 1.2 GB run: an argv scan missed the job and found
#    only its monitor. Enumerate by CWD instead -- the kernel's answer, independent of how the process was
#    invoked -- in one lsof call (~0.25s). argv is still reported, as a LABEL, never as the identity.
REPO = "/Users/sumit/Github/SpaceTime"
procs = []
seen = set()
cwd_out = sh(f"lsof -a -d cwd -u $(id -un) -Fpn 2>/dev/null || true")
cur = None
for ln in cwd_out.splitlines():
    if ln.startswith("p"):
        cur = ln[1:]
    elif ln.startswith("n") and cur and cur.isdigit():
        if not ln[1:].startswith(REPO):
            continue
        pid = int(cur)
        if pid in seen or pid in ancestors or pid in (self_pid, os.getpid()):
            continue
        stat = sh(f"ps -o ppid=,rss=,%cpu=,command= -p {pid}").strip()
        if not stat:
            continue
        parts = stat.split(None, 3)
        if len(parts) < 4:
            continue
        ppid, rss, cpu, cmd = int(parts[0]), parts[1], parts[2], parts[3]
        if ppid in (self_pid, os.getpid()) or "keepalive.sh" in cmd:   # our own subprocesses
            continue
        seen.add(pid)
        try: cpu_f = float(cpu)
        except ValueError: cpu_f = 0.0
        procs.append({"pid": pid, "rss_mb": round(int(rss)/1024, 1) if rss.isdigit() else None,
                      "cpu_pct": cpu_f, "cmd": cmd[:70]})
vm = sh("vm_stat"); ps_size = 16384
free_gb = None
try:
    import re
    ps_size = int(re.search(r"page size of (\d+)", vm).group(1))
    fr = int(re.search(r"Pages free:\s+(\d+)", vm).group(1))
    ina = int(re.search(r"Pages inactive:\s+(\d+)", vm).group(1))
    free_gb = round((fr + ina) * ps_size / 1073741824, 2)
except Exception:
    pass

n_active = sum(1 for x in procs if (x.get("cpu_pct") or 0) > 5.0)
d["measured"] = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "n_procs": len(procs), "n_active": n_active,
                 "procs": sorted(procs, key=lambda x: -(x.get("cpu_pct") or 0))[:5],
                 "machine_free_plus_inactive_gb": free_gb,
                 "note": ("DERIVED every tick by CWD (not argv -- silent_nulls 46/49), excluding this script's "
                          "own lineage. n_procs = everything of ours rooted in the repo, INCLUDING idle shells; "
                          "n_active = those over 5% CPU. Both reported because collapsing them forces a choice "
                          "between over- and under-counting. Jitters if real.")}

# FLAT MIRRORS of the derived fields, at top level, under the names the shared reader expects.
# Nesting them under `measured` made them invisible from outside: a peer sizing a memory decision against
# this file got None. Correct-but-unreadable is a real cost to someone else's scheduling, so the canonical
# names are published flat as well. `measured` stays as the authoritative, self-describing block.
d["job_pids"] = [q["pid"] for q in procs]
d["rss_total_mb"] = round(sum((q.get("rss_mb") or 0) for q in procs), 1)
d["mem_free_gb"] = free_gb

# LIVENESS TOKEN. Our fields are derived and therefore cannot be produced without looking -- but a reader
# cannot verify that from outside, and with no token the only evidence of life is a timestamp, which is
# exactly what a bumping loop can forge. A published, ps-resolvable pid makes the correctness externally
# checkable rather than something a peer has to take on trust.
d["writer_pid"] = self_pid
d["heartbeat_pid"] = self_pid          # both spellings: peers use different field names
# 5. A WIDENED SCAN SILENTLY CHANGED A DOWNSTREAM LABEL. `state` read "running if procs else idle", which was
#    correct while `procs` came from an argv match on this repo's scripts. Switching to CWD enumeration (fix 4)
#    correctly widened DETECTION and thereby broke the LABEL: an idle login shell whose cwd is the repo made
#    this publish `state: running` with nothing computing -- to sister sessions deciding whether the machine is
#    free, that reads as "tabula is busy". n_active existed for exactly this and `state` was never pointed at
#    it. **Fixing an input can corrupt a consumer that was correct under the old semantics**, and nothing here
#    failed: the field was derived, fresh, and jittering throughout.
n_active_now = sum(1 for q in procs if (q.get("cpu_pct") or 0) > 5.0)
d["state"] = "running" if n_active_now else "idle"       # DERIVED from CPU, not from mere presence in the repo
# heavy = memory actually held by ACTIVE work; an idle shell rooted here must never make us look heavy.
d["heavy"] = bool(any((q.get("rss_mb") or 0) > 1500 and (q.get("cpu_pct") or 0) > 5.0 for q in procs))

# --- DECLARED: cannot be refreshed by any heartbeat, so label it and age it ---
if "detail" in d and "declared_at" not in d:
    d["declared_at"] = d.get("updated", now.strftime("%Y-%m-%dT%H:%M:%SZ"))
try:
    da = datetime.datetime.strptime(d["declared_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    d["declared_age_s"] = int((now - da).total_seconds())
except Exception:
    d["declared_age_s"] = None
d["field_semantics"] = ("`state`/`heavy`/`measured` are DERIVED from the machine each tick -- schedule against "
                        "these. `detail` is DECLARED by the agent and is stale the moment work moves on; "
                        "`declared_age_s` says how stale. `updated` is a claim about ALL fields, never bumped "
                        "alone.")
d["updated"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
d.setdefault("stale_after_s", 120)
json.dump(d, open(p, "w"), indent=2)
PY
  fi
  sleep 30
done
echo "keepalive ended after ${HOURS}h"
