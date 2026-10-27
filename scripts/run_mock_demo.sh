#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export USE_MOCK="${USE_MOCK:-1}"
python3 -m whytrace status
python3 -m whytrace ask "Which zones have the highest crash density and which companies operate there?"
python3 -m whytrace audit --limit 12
