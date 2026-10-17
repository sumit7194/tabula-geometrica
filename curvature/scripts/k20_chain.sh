#!/bin/bash
# K20 overnight chain (2026-10-17, user said resume): screen -> C3 supplement -> official analysis -> C0 add-on.
# Each stage runs under watch_footprint (<=4 workers, MAXMB 2048, MINDISK 5) and must end "exit=0" or the chain stops.
C=/Users/sumit/Github/SpaceTime/curvature
PY=$C/.venv314ob/bin/python
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MAXMB=2048 MINFREEPCT=10 MINDISK=5
stage() {   # stage <log> <args...>
  local log=$1; shift
  echo "=== STAGE $* $(date) ===" >> $C/results/197_chain.log
  nice -n 10 $C/scripts/watch_footprint.sh $log -- $PY -u $C/scripts/197_k20_mn_screen.py "$@" --workers 4
  if tail -1 $log | grep -q "exit=0"; then echo "  ok $(date)" >> $C/results/197_chain.log
  else echo "  FAILED ($(tail -1 $log)) -- chain stopped $(date)" >> $C/results/197_chain.log; exit 1; fi
}
stage $C/results/197_screen_run.log --screen p1 p2 F5R
stage $C/results/197_c3s_run.log --c3-supplement
stage $C/results/197_analysis_run.log --analyze p1 p2 F5R
stage $C/results/197_c0_run.log --analyze-c0
echo "=== CHAIN DONE $(date) ===" >> $C/results/197_chain.log
