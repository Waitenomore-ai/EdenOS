#!/usr/bin/env bash
set -euo pipefail
package_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$package_dir"
export XDG_CONFIG_HOME="$package_dir/demo-config"
mkdir -p "$XDG_CONFIG_HOME"
eden_python="$package_dir/.venv/bin/python"
if [ ! -x "$eden_python" ]; then
  eden_python="python3"
fi
if ! "$eden_python" -c "import PySide6.QtWidgets" >/dev/null 2>&1; then
  echo "PySide6 is missing. See README.md for development setup." >&2
  exit 2
fi
exec "$eden_python" -m native_eden_v0.window
