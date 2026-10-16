#!/bin/zsh
# Chain A relaunch at 937e5c0 (amendment 1). Waits for the first launcher (chain B) before the final comparison.
W=/Users/sumit/Github/SpaceTime_repro_ob/curvature
PY=/Users/sumit/Github/SpaceTime/curvature/.venv314ob/bin/python
L=$W/results/repro_logs
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MAXMB=6144 MINFREEPCT=8 MINDISK=5
cd $W
for m in probe production rank6 export-farfield rank6-strong; do
  echo "START 193_$m $(date '+%F %T')" >> $L/chain_A2.status
  bash scripts/watch_footprint.sh $L/193_$m.log -- $PY -u scripts/193_ts2_screen.py --$m
  echo "END 193_$m $(date '+%F %T') $(tail -1 $L/193_$m.log)" >> $L/chain_A2.status
done
echo "CHAIN A2 DONE $(date '+%F %T')" >> $L/chain_A2.status
while ps -p 71758 >/dev/null 2>&1; do sleep 30; done
$PY -I scripts/repro_openblas_compare.py $W/results cd3b89d > $L/compare_final.txt 2>&1
echo "FINAL DONE $(date '+%F %T')" >> $L/chain_A2.status
