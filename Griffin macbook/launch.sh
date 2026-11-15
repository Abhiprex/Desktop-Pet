#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Desktop Pet Griffin - macOS Terminal Launcher (MacBook Air M1 / Apple Silicon)
# -----------------------------------------------------------------------------
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "  🐾  Desktop Pet Griffin - macOS M1 Edition  🐾 "
echo "=================================================="

PYTHON_BIN=""
if [ -f "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
elif [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON_BIN="/opt/homebrew/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="$(command -v python3)"
elif [ -x "/usr/local/bin/python3" ]; then
    PYTHON_BIN="/usr/local/bin/python3"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ Error: Python 3 was not found."
    echo "Install Python 3 with Homebrew:  brew install python"
    echo "Or download from: https://www.python.org/downloads/macos/"
    exit 1
fi

echo "Using Python: $PYTHON_BIN"

if ! "$PYTHON_BIN" -c "import PyQt6, PIL" &>/dev/null; then
    echo "📦 Installing PyQt6 and Pillow for Apple Silicon..."
    "$PYTHON_BIN" -m pip install -r requirements.txt
fi

echo "✨ Starting your Desktop Pet..."
exec "$PYTHON_BIN" run_pet.py "$@"
