#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-}"
shift || true
if [[ "$MODE" != "before" && "$MODE" != "after" ]] || [[ $# -lt 4 || $# -gt 5 ]]; then
  echo 'Usage: screenshot.sh before|after NAME URL WIDTH HEIGHT [legacy-min-luminance]' >&2
  exit 2
fi
if [[ ! "$1" =~ ^[a-zA-Z0-9][a-zA-Z0-9_-]*$ ]]; then
  echo 'NAME must contain only letters, numbers, underscores, and hyphens.' >&2
  exit 2
fi
if [[ $# -eq 5 ]]; then
  echo 'The old brightness threshold is ignored; inspect the screenshot and layout checks.' >&2
fi
if [[ -x "$ROOT/.venv/Scripts/python.exe" ]]; then
  TASK_PYTHON="$ROOT/.venv/Scripts/python.exe"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then
  TASK_PYTHON="$ROOT/.venv/bin/python"
else
  echo 'Create the project .venv and install requirements.txt first.' >&2
  exit 1
fi
exec "$TASK_PYTHON" "$ROOT/.cdp-shot.py" "$2" "$3" "$4" "$ROOT/reports/screenshots/$MODE/$1.png"
