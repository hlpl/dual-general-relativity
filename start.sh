#!/bin/sh
set -e
cd "$(dirname "$0")"
# Kill any stale DGR server still holding the port (this is what shows old/JSON pages)
if command -v fuser >/dev/null 2>&1; then fuser -k 5000/tcp 5001/tcp 5002/tcp 2>/dev/null || true; fi
pkill -f dual_general_relativity 2>/dev/null || true
sleep 1
find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
if [ ! -x .venv/bin/python ]; then echo "Creating .venv ..."; python3 -m venv .venv; fi
.venv/bin/pip install --quiet flask sympy numpy
echo "Starting - open the URL printed below (NOT an /api/... URL)"
PYTHONPATH="$PWD/src:$PYTHONPATH" exec .venv/bin/python -m dual_general_relativity "$@"
