#!/bin/bash
# G-sym fix round: OWNS the full gen->merge->train order so no stale bank can leak
# in. (v1 bug: it waited on shard-file EXISTENCE, but old shards were already on
# disk, so it merged stale data and trained on it — "file exists" != "file fresh".)
# Detached:  nohup ./scripts/28c_fixround_driver.sh > results/28c_driver.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
PY=./.venv/bin/python
R=results

echo "[driver] deleting any old banks so freshness is guaranteed"
rm -f $R/25_bank_s{1,2,3,4}.npz $R/25_bank_s{1,2,3,4}.meta.json \
      $R/25_bank_120k.npz $R/25_bank_120k.meta.json \
      $R/25_bank.npz $R/25_bank.meta.json \
      $R/25_bank_probe.npz $R/25_bank_probe.meta.json \
      $R/25_bank_wide.npz $R/25_bank_wide.meta.json

echo "[driver] generating fresh banks (this script owns the order)"
for s in 1 2 3 4; do
  $PY scripts/25_worldgen.py --n-per-family 3750 --seed $s --out $R/25_bank_s$s.npz &
done
$PY scripts/25_worldgen.py --n-per-family 3000 --seed 0 --out $R/25_bank.npz &
$PY scripts/25_worldgen.py --n-per-family 200 --seed 123 --emit-qlabels --out $R/25_bank_probe.npz &
$PY scripts/25_worldgen.py --n-per-family 250 --seed 99 --widen 1.25 --out $R/25_bank_wide.npz &
wait
echo "[driver] all gens done; merging 120k"
$PY scripts/25b_merge_banks.py $R/25_bank_s1.npz $R/25_bank_s2.npz \
    $R/25_bank_s3.npz $R/25_bank_s4.npz --out $R/25_bank_120k.npz || exit 1

echo "[driver] retrain SymGeneralist (unique tags), tag _sym2"
$PY scripts/28_symmetric_generalist.py --device mps --steps 150000 \
    --bank $R/25_bank_120k.npz --val-bank $R/25_bank.npz --tag _sym2 || exit 1
echo "[driver] DONE — A1 in $R/28_g1_sym2.json, model 28_symgen_sym2.pt"
