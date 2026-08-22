#!/usr/bin/env bash
# Session keepalive + self-refreshing coordination heartbeat.
#
# LIVES IN THE REPO, not in a scratch dir, because it has now failed twice for reasons a scratch file cannot
# avoid: once by holding a startup SNAPSHOT and silently reverting every status update for ten hours
# (silent_nulls entry 32), and once by simply vanishing when the session's scratchpad was wiped. Session
# plumbing that other sessions depend on is infrastructure, and infrastructure that is not versioned is the
# half that goes wrong -- the night's most-repeated finding.
#
# TWO PROPERTIES THAT MUST NOT REGRESS:
#   1. RE-READ THE FILE EVERY TICK. Never cache it. Caching makes the timestamp truthful while the content
#      freezes, which converts a visible failure into an invisible one -- every observable says it worked.
#   2. REWRITE `updated` EVERY TICK, not only on state change, so a status nobody maintains announces itself.
# Verify after any edit by writing a distinctive `detail`, waiting past one tick, and reading it back.
set -eu
S=/Users/sumit/Github/.claude-coordination/tabula.status
HOURS="${1:-10}"
END=$(( $(date +%s) + HOURS * 3600 ))
while [ "$(date +%s)" -lt "$END" ]; do
  if [ -f "$S" ]; then
    python3 - "$S" << 'PY' 2>/dev/null || true
import json, sys, datetime
p = sys.argv[1]
try:
    d = json.load(open(p))            # re-read every tick: no snapshot, ever
except Exception:
    sys.exit(0)
d["updated"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
d.setdefault("stale_after_s", 120)    # machine-checkable contract, not a prose warning
json.dump(d, open(p, "w"), indent=2)
PY
  fi
  sleep 30
done
echo "keepalive ended after ${HOURS}h"
