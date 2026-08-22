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
#
# ── THE STRUCTURAL FIX: separate DECLARED from DERIVED ─────────────────────────────────────────────────
# `state`/`detail` are DECLARED -- a human/agent types them and they are stale the moment work moves on. No
# heartbeat can refresh a declaration. So they are marked as declarations, carry their own age, and are never
# what a reader should schedule against. `measured` is DERIVED from the machine every tick; it cannot be
# faked by a loop that does not actually look, and its numbers JITTER, which is what distinguishes a real
# heartbeat from a bumping one.
set -eu
S=/Users/sumit/Github/.claude-coordination/tabula.status
HOURS="${1:-10}"
END=$(( $(date +%s) + HOURS * 3600 ))
SELF=$$
while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$S" ]; then
    python3 - "$S" "$SELF" << 'PY' 2>/dev/null || true
import json, os, subprocess, sys, datetime
p, self_pid = sys.argv[1], int(sys.argv[2])
try:
    d = json.load(open(p))                       # re-read every tick: no snapshot, ever
except Exception:
    sys.exit(0)
now = datetime.datetime.now(datetime.timezone.utc)

def sh(c):
    try: return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=8).stdout
    except Exception: return ""

# --- DERIVED: measured fresh every tick, excluding this script and its children ---
procs = []
for ln in sh("pgrep -fl 'SpaceTime/curvature' || true").strip().splitlines():
    pid = ln.split()[0] if ln.split() else ""
    if not pid.isdigit() or int(pid) in (self_pid, os.getpid()):
        continue
    if "keepalive.sh" in ln:                     # never count the monitor as activity
        continue
    rss = sh(f"ps -o rss= -p {pid}").strip()
    procs.append({"pid": int(pid), "rss_mb": round(int(rss)/1024, 1) if rss.isdigit() else None,
                  "cmd": " ".join(ln.split()[1:])[:70]})
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

d["measured"] = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "n_procs": len(procs),
                 "procs": procs[:5], "machine_free_plus_inactive_gb": free_gb,
                 "note": "DERIVED every tick from ps/vm_stat, excluding this keepalive. Jitters if real."}
d["state"] = "running" if procs else "idle"      # DERIVED, not preserved from a declaration
d["heavy"] = bool(any((q.get("rss_mb") or 0) > 1500 for q in procs))

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
