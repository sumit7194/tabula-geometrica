#!/bin/bash
# Phase G data-scaling driver: wait for the 4 worldgen shards, merge, then run
# the 48k and 120k arms sequentially (fresh init each, shared seed-0 val set).
# Launch detached from curvature/:  nohup ./scripts/26b_scaling_driver.sh > results/26b_driver.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
PY=./.venv/bin/python

echo "[driver] waiting for shards..."
for i in $(seq 1 240); do
  ok=1
  for s in 1 2 3 4; do [ -f "results/25_bank_s$s.npz" ] || ok=0; done
  [ "$ok" = 1 ] && break
  sleep 60
done
[ "$ok" = 1 ] || { echo "[driver] TIMEOUT waiting for shards"; exit 1; }
sleep 30  # let the last npz finish writing

echo "[driver] merging banks"
$PY scripts/25b_merge_banks.py results/25_bank_s1.npz results/25_bank_s2.npz --out results/25_bank_48k.npz || exit 1
$PY scripts/25b_merge_banks.py results/25_bank_s1.npz results/25_bank_s2.npz results/25_bank_s3.npz results/25_bank_s4.npz --out results/25_bank_120k.npz || exit 1

echo "[driver] arm-48k starting"
$PY scripts/26_generalist.py --device mps --steps 150000 \
  --bank results/25_bank_48k.npz --val-bank results/25_bank.npz --tag _48k || exit 1

echo "[driver] arm-120k starting"
$PY scripts/26_generalist.py --device mps --steps 150000 \
  --bank results/25_bank_120k.npz --val-bank results/25_bank.npz --tag _120k || exit 1

echo "[driver] DONE — scaling curve points in results/26_g1_48k.json + 26_g1_120k.json"
