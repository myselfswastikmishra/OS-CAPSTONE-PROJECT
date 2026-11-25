#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then echo "Python 3 not found. Install Python 3 and retry." >&2; exit 1; fi
if ! "$PYTHON_BIN" -c 'import psutil, matplotlib' >/dev/null 2>&1; then
  echo "Installing project dependencies..."
  "$PYTHON_BIN" -m pip install -r requirements.txt
fi
exec "$PYTHON_BIN" src/monitor.py "$@"
