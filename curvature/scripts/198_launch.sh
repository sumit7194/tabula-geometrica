#!/usr/bin/env bash
# §198 unattended launcher. Detaches into its own session (survives the Claude app closing), keeps the Mac awake,
# runs the scan at nice 10 under the footprint watchdog, and RESUMES after a watchdog kill or crash (finished jobs
# are skipped). Gives up after MAX_TRIES attempts, or at once when the run reports DONE.
#   start:  nohup /Users/sumit/Github/SpaceTime/curvature/scripts/198_launch.sh >/dev/null 2>&1 &
#   watch:  cat /Users/sumit/Github/SpaceTime/curvature/results/198_status.json
#   stop:   kill $(cat /Users/sumit/Github/SpaceTime/curvature/results/198_launcher.pid)   (stops the attempt too)
#   args:   [--smoke]  (test only: toy run into results/198_smoke)
set -u
C=/Users/sumit/Github/SpaceTime/curvature
if [ -z "${TABULA198_DETACHED:-}" ]; then
  export TABULA198_DETACHED=1
  exec /usr/bin/python3 -c 'import os, sys; os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' "$0" "$@"
fi
MODE="--run"; TAG=""
[ "${1:-}" = "--smoke" ] && { MODE="--smoke"; TAG="_smoke"; }
STATUS=$C/results/198_status.json; [ -n "$TAG" ] && STATUS=$C/results/198_smoke/198_status.json
PIDF="$C/results/198_launcher$TAG.pid"
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then   # single instance: two copies would race on files
  echo "$(date '+%F %T') REFUSED: launcher $(cat "$PIDF") already running" >> "$C/results/198_launcher$TAG.log"; exit 3
fi
echo $$ > "$PIDF"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MAXMB=${MAXMB:-3000} MINDISK=${MINDISK:-5} MINFREEPCT=${MINFREEPCT:-10}
MAX_TRIES=${MAX_TRIES:-6}
G=""
# stopping the launcher stops its current attempt too (each attempt has its own process group, so killing only the
# launcher's group would leave the scan running -- found in the lock test)
_stop() { [ -n "$G" ] && { kill -TERM -- -$G 2>/dev/null; sleep 3; kill -KILL -- -$G 2>/dev/null; }
          echo "$(date '+%F %T') STOPPED by signal" >> "$C/results/198_launcher$TAG.log"; rm -f "$PIDF"; exit 143; }
trap _stop TERM INT HUP
for n in $(seq 1 "$MAX_TRIES"); do
  LOG=$C/results/198_run${TAG}_try$n.log
  echo "$(date '+%F %T') attempt $n start" >> "$C/results/198_launcher$TAG.log"
  # each attempt in its OWN process group, killed whole before any retry: if only the watchdog dies, its scan and
  # pool workers would otherwise run on unwatched and race the next attempt (found in the launcher test)
  /usr/bin/python3 -c 'import os, sys; os.setsid(); os.execv(sys.argv[1], sys.argv[1:])' \
    /usr/bin/caffeinate -i /usr/bin/nice -n 10 "$C/scripts/watch_footprint.sh" "$LOG" -- \
    "$C/.venv314ob/bin/python" -u "$C/scripts/198_ts_layer_scan.py" $MODE --workers 3 &
  G=$!
  wait $G; wait $G 2>/dev/null                            # a trapped signal interrupts the first wait
  kill -TERM -- -$G 2>/dev/null; sleep 3; kill -KILL -- -$G 2>/dev/null
  echo "$(date '+%F %T') attempt $n end (group $G cleaned): $(tail -1 "$LOG")" >> "$C/results/198_launcher$TAG.log"
  if grep -q '"phase": "DONE"' "$STATUS" 2>/dev/null; then
    echo "$(date '+%F %T') DONE" >> "$C/results/198_launcher$TAG.log"; exit 0
  fi
  sleep $(( ${BACKOFF:-300} * n ))                                  # back off: 5, 10, 15 ... min (lets a memory spike pass)
done
echo "$(date '+%F %T') GAVE UP after $MAX_TRIES attempts" >> "$C/results/198_launcher$TAG.log"
exit 1
