#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_CMD=python3
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  PYTHON_CMD=python
fi

if [ ! -f ".venv/bin/python" ]; then
  echo "Creating virtual environment .venv..."
  "$PYTHON_CMD" -m venv .venv
fi

source .venv/bin/activate

python -m pip install --upgrade pip >/dev/null 2>&1
if [ -f "requirements.txt" ]; then
  echo "Installing requirements..."
  python -m pip install -r requirements.txt
fi

if [ ! -f ".env" ]; then
  if [ -f ".env.example" ]; then
    cp .env.example .env
    echo "Created .env from .env.example. Edit it with your API keys before use."
  else
    echo "Warning: .env not found and .env.example not present."
  fi
fi

mkdir -p "$SCRIPT_DIR/data/logs/cache"

echo "Launching Software-AI..."
exec python main.py "$@"
