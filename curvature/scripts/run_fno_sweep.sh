#!/usr/bin/env bash
# FNO sweep for the Phase-F F1 magnitude gap (run on the L4 VM).
# Methodology: ONE knob = Fourier modes; 3 seeds for variance; fixed longer budget (no other knob moves).
# P0/F2/F3/F4 already pass at modes=14 on MPS; this targets the absolute F1 trajectory-MSE gate (1e-3, floor 1.2e-4).
set -e
cd "$(dirname "$0")/.."          # -> curvature/
. .venv/bin/activate
STEPS=${STEPS:-12000}
MODES=${MODES:-"14 24"}          # current vs (near-)max Fourier modes on the 48-grid
SEEDS=${SEEDS:-"0 1 2"}
for m in $MODES; do
  for s in $SEEDS; do
    tag="_m${m}_s${s}"
    echo "================ arm modes=$m seed=$s steps=$STEPS ================"
    python scripts/100_fno_law.py --modes "$m" --seed "$s" --steps "$STEPS" --overfit-steps 0 \
      --device cuda --tag "$tag" 2>&1 \
      | grep -E "device=|resumed|train\] step|P1 F1|P2 F2|F3 super|P3 F4|saved" || true
  done
done
echo "================ FNO SWEEP DONE ================"
# aggregate the arms
python - <<'PY'
import json, glob, os
rows=[]
for f in sorted(glob.glob("results/100_fno_law_m*_s*.json")):
    d=json.load(open(f))
    rows.append((d.get("modes"), d.get("seed"), d.get("F1_mse"), d.get("F2_cos"), d.get("F3_cos"), d.get("F4_blind")))
print(f"\n{'modes':>5} {'seed':>4} {'F1_mse':>10} {'F2_cos':>8} {'F3_cos':>8} {'F4_blind':>9}")
for r in rows:
    print(f"{r[0]:>5} {r[1]:>4} {r[2]:>10.2e} {r[3]:>8.4f} {r[4]:>8.4f} {r[5]:>9.2e}")
PY
