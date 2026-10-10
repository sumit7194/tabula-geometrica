#!/usr/bin/env bash
# Run a command under a whole-process-tree footprint watchdog (house rule, 2026-09-24).
# usage: MAXMB=5120 watch_footprint.sh LOG -- cmd...
# Samples top MEM + CMPRS (never RSS: compressed memory hides from RSS) for the command and its children every
# 2 s. Kills the tree if it exceeds MAXMB, free disk < 5 GB, or free swap < 512 MB. Writes the peak and the exit
# code to LOG, so a death always says why.
# The tree = $PID and ALL its descendants (measured and killed together).
# MINDISK (GB, default 5); MINFREEPCT (memory_pressure system-free %, replaces the swap trigger when set).
LOG=$1; shift; shift
: > "$LOG"; "$@" >> "$LOG" 2>&1 &   # O_APPEND: the child cannot overwrite the watchdog lines
PID=$!
PEAK=0
# Kill the WHOLE tree, deepest first. Killing only $PID orphans pool workers, which keep running unwatched and
# write into the next run's log (found 2026-10-11: §195 G0's killed run left 3 workers alive, one at 1.4 GB).
killtree() { for c in $(pgrep -P "$1"); do killtree "$c"; done; kill "$1" 2>/dev/null; }
desc() { for c in $(pgrep -P "$1"); do echo "$c"; desc "$c"; done; }
tomb() { v=$1; case $v in *G) echo "${v%G}*1024" | bc;; *M) echo "${v%M}";; *K) echo "${v%K}/1024" | bc -l;; *) echo 0;; esac; }
while kill -0 $PID 2>/dev/null; do
  TOT=0
  for p in $PID $(desc $PID); do
    set -- $(top -l 1 -pid $p -stats pid,mem,cmprs 2>/dev/null | tail -1)
    [ "$1" = "$p" ] || continue
    TOT=$(echo "$TOT + $(tomb "${2%[+-]}") + $(tomb "${3%[+-]}")" | bc -l)
  done
  PEAK=$(echo "if ($TOT > $PEAK) $TOT else $PEAK" | bc -l)
  DISK=$(df -g / | tail -1 | awk '{print $4}')
  SWF=$(sysctl -n vm.swapusage | sed -E 's/.*free = ([0-9.]+)M.*/\1/')
  MP=$(memory_pressure -Q 2>/dev/null | sed -nE 's/.*free percentage: ([0-9]+)%.*/\1/p')
  if [ "$(echo "$TOT > ${MAXMB:-999999}" | bc)" = 1 ] || [ "$DISK" -lt "${MINDISK:-5}" ] \
     || { [ -z "${MINFREEPCT:-}" ] && [ "$(echo "$SWF < 512" | bc)" = 1 ]; } \
     || { [ -n "${MINFREEPCT:-}" ] && [ -n "$MP" ] && [ "$MP" -lt "$MINFREEPCT" ]; }; then
    echo "WATCHDOG KILL tree=${TOT}MB disk=${DISK}G swapfree=${SWF}M sysfree=${MP}%" >> "$LOG"
    killtree $PID
  fi
  sleep 2
done
wait $PID; EC=$?
echo "FOOTPRINT peak_tree_MEM+CMPRS_MB=$(printf %.0f $PEAK) exit=$EC" >> "$LOG"
