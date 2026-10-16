#!/bin/zsh
# OpenBLAS reproducibility rerun (prereg: notes/openblas_repro_193_194_prereg.md, 5a2a42a). Launched by The Bridge.
W=/Users/sumit/Github/SpaceTime_repro_ob/curvature
PY=/Users/sumit/Github/SpaceTime/curvature/.venv314ob/bin/python
L=$W/results/repro_logs
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MAXMB=6144 MINFREEPCT=8 MINDISK=5
cd $W
step() { local name=$1; shift; echo "START $name $(date '+%F %T')" >> $L/chain_$CH.status
  bash scripts/watch_footprint.sh $L/$name.log -- "$@"; echo "END $name $(date '+%F %T') $(tail -1 $L/$name.log)" >> $L/chain_$CH.status; }
chainA() { CH=A; for m in probe production rank6 export-farfield rank6-strong; do step 193_$m $PY -u scripts/193_ts2_screen.py --$m; done; echo "CHAIN A DONE $(date '+%F %T')" >> $L/chain_A.status; }
chainB() { CH=B; step 194_pilot $PY -u scripts/194_orbit_dimension.py --pilot; step 194b_diagnose $PY -u scripts/194b_diagnose_g0.py; echo "CHAIN B DONE $(date '+%F %T')" >> $L/chain_B.status; }
chainA & chainB & wait
$PY -I scripts/repro_openblas_compare.py $W/results cd3b89d > $L/compare.txt 2>&1
echo "ALL DONE $(date '+%F %T')" >> $L/chain_A.status
