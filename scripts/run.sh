#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${SERVO_ENV:-$HOME/servo-env}"
export PAN_TILT_CONFIG="${PAN_TILT_CONFIG:-$HOME/pan_tilt_config.json}"

cd "$ROOT_DIR"

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Missing virtual environment: $VENV_DIR"
  echo "Run scripts/install.sh first."
  exit 1
fi

exec "$VENV_DIR/bin/python" src/app.py
