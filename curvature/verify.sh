#!/bin/bash
# Regression gate: re-runs every probe against saved models, asserts the
# pre-registered thresholds. Usage: ./verify.sh
cd "$(dirname "$0")"
exec .venv/bin/python scripts/verify_gates.py
