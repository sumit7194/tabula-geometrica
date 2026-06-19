#!/usr/bin/env bash
# FNO GRID-RESOLUTION sweep for the Phase-F F1 magnitude gap (run on the L4 VM).
# The modes sweep (run_fno_sweep.sh) showed F1 saturates at ~0.015 and is NOT modes/training-limited at the
# 48-grid: modes 24 == modes 14, because 24 is the 48-grid Nyquist limit -- the grid itself band-limits the
# sharp near-mass field. Hypothesis: a FINER grid (with modes scaled to its full Nyquist band) resolves the
# field MAGNITUDE near masses and drops F1 toward the 1e-3 gate (oracle floor 1.2e-4).
# ONE knob = grid resolution; modes follow as grid//2 (full spectral capacity); 3 seeds. Baseline grid=48
# modes=24 (F1 ~0.0150) already banked from the modes sweep.
set -e
cd "$(dirname "$0")/.."          # -> curvature/
. .venv/bin/activate
STEPS=${STEPS:-12000}
SEEDS=${SEEDS:-"0 1 2"}
for g in 64 96; do
  if [ "$g" = 64 ]; then m=32; else m=48; fi   # modes = grid//2 (the grid's full Nyquist band)
  for s in $SEEDS; do
    tag="_g${g}_s${s}"
    echo "================ grid=$g modes=$m seed=$s steps=$STEPS ================"
    python scripts/100_fno_law.py --grid "$g" --modes "$m" --seed "$s" --steps "$STEPS" \
      --overfit-steps 0 --device cuda --tag "$tag" 2>&1 \
      | grep -E "device=|resumed|train\] step|P1 F1|P2 F2|F3 super|P3 F4|saved" || true
  done
done
echo "================ GRID SWEEP DONE ================"
python - <<'PY'
import json, glob
print(f"\n{'grid':>5} {'modes':>5} {'seed':>4} {'F1_mse':>10} {'F2_cos':>8} {'F3_cos':>8}")
for f in sorted(glob.glob("results/100_fno_law_g*_s*.json")):
    d=json.load(open(f))
    print(f"{d.get('grid'):>5} {d.get('modes'):>5} {d.get('seed'):>4} {d.get('F1_mse'):>10.2e} {d.get('F2_cos'):>8.4f} {d.get('F3_cos'):>8.4f}")
print("baseline grid=48 modes=24: F1 ~0.0150 (1e-3 gate, 1.2e-4 oracle floor)")
PY
