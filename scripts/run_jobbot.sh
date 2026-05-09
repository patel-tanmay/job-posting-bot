#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

export HOME="${HOME:-/Users/tanmaypatel}"
export TMPDIR="${TMPDIR:-/tmp}"
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin"

cd "$PROJECT_DIR"

if [ -f "$PROJECT_DIR/venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$PROJECT_DIR/venv/bin/activate"
fi

"$PROJECT_DIR/venv/bin/python" -m jobbot run --config config.yaml
