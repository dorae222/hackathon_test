#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting AI service..."

MODEL_PTH_PATH="${MODEL_PTH_PATH:-/app/models/dog_breed_classifier.pth}"

if [ "${TRAIN_ON_START:-0}" = "1" ] && [ ! -f "$MODEL_PTH_PATH" ]; then
  echo "[entrypoint] TRAIN_ON_START=1 and model not found. Running quick training..."
  # Quick training defaults (override via env if needed)
  export MAX_TRAIN_SAMPLES="${MAX_TRAIN_SAMPLES:-20}"
  export PRETRAINED="${PRETRAINED:-1}"
  export FREEZE_BACKBONE="${FREEZE_BACKBONE:-1}"
  export EPOCHS="${EPOCHS:-1}"
  export BATCH_SIZE="${BATCH_SIZE:-8}"
  python -m app.train || echo "[entrypoint] Training failed or skipped. Continuing to serve API."
fi

echo "[entrypoint] Launching API server"
exec gunicorn -c app/gunicorn_conf.py app.main:app
