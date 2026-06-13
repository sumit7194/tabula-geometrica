#!/bin/bash
# G-sym fix round: wait for the unique-tag banks, merge 120k, retrain SymGeneralist.
# Detached:  nohup ./scripts/28c_fixround_driver.sh > results/28c_driver.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
PY=./.venv/bin/python

echo "[driver] waiting for shards + val bank..."
for i in $(seq 1 120); do
  ok=1
  for f in results/25_bank_s1.npz results/25_bank_s2.npz results/25_bank_s3.npz \
           results/25_bank_s4.npz results/25_bank.npz; do
    [ -f "$f" ] || ok=0
  done
  [ "$ok" = 1 ] && break
  sleep 60
done
[ "$ok" = 1 ] || { echo "[driver] TIMEOUT"; exit 1; }
sleep 20  # let final npz flush

echo "[driver] merging 120k"
$PY scripts/25b_merge_banks.py results/25_bank_s1.npz results/25_bank_s2.npz \
    results/25_bank_s3.npz results/25_bank_s4.npz --out results/25_bank_120k.npz || exit 1

echo "[driver] retrain SymGeneralist (unique tags), tag _sym2"
$PY scripts/28_symmetric_generalist.py --device mps --steps 150000 \
    --bank results/25_bank_120k.npz --val-bank results/25_bank.npz --tag _sym2 || exit 1
echo "[driver] DONE — A1 in results/28_g1_sym2.json, model 28_symgen_sym2.pt"
