import os
import shutil
from PIL import Image

BASE_DIR = r"D:\Personal Project\desktop pet macbook"

# 1. Generate pet.icns
cute_idle = os.path.join(BASE_DIR, "sprites", "cute", "idle_1.png")
icns_path = os.path.join(BASE_DIR, "pet.icns")
img = Image.open(cute_idle).convert("RGBA")
img_1024 = img.resize((1024, 1024), resample=Image.Resampling.NEAREST)
img_1024.save(icns_path, format="ICNS")
print("pet.icns created:", os.path.getsize(icns_path), "bytes")

# 2. Build Desktop Pet.app bundle
app_dir = os.path.join(BASE_DIR, "Desktop Pet.app")
contents_dir = os.path.join(app_dir, "Contents")
macos_dir = os.path.join(contents_dir, "MacOS")
resources_dir = os.path.join(contents_dir, "Resources")

os.makedirs(macos_dir, exist_ok=True)
os.makedirs(resources_dir, exist_ok=True)

shutil.copy2(icns_path, os.path.join(resources_dir, "pet.icns"))

# PkgInfo
with open(os.path.join(contents_dir, "PkgInfo"), "wb") as f:
    f.write(b"APPL????")

# Info.plist
plist_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Desktop Pet</string>
    <key>CFBundleDisplayName</key>
    <string>Desktop Pet Griffin</string>
    <key>CFBundleIdentifier</key>
    <string>com.cozypet.desktop.griffin</string>
    <key>CFBundleVersion</key>
    <string>4.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>4.0.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>CFBundleExecutable</key>
    <string>Desktop Pet</string>
    <key>CFBundleIconFile</key>
    <string>pet.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSSupportsAutomaticGraphicsSwitching</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
""".replace("\r\n", "\n")

with open(os.path.join(contents_dir, "Info.plist"), "w", encoding="utf-8", newline="\n") as f:
    f.write(plist_content)

# Launcher executable script inside MacOS/
mac_exec_content = """#!/usr/bin/env bash
# macOS Application Bundle entrypoint for Desktop Pet Griffin
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$DIR"

PYTHON_BIN=""
if [ -f "$DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$DIR/venv/bin/python3"
elif [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON_BIN="/opt/homebrew/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON_BIN="$(command -v python3)"
elif [ -x "/usr/local/bin/python3" ]; then
    PYTHON_BIN="/usr/local/bin/python3"
fi

if [ -z "$PYTHON_BIN" ]; then
    osascript -e 'display alert "Python 3 Required" message "Please install Python 3 on your Mac via Homebrew (brew install python) or from python.org to run Desktop Pet."'
    exit 1
fi

if ! "$PYTHON_BIN" -c "import PyQt6, PIL" &>/dev/null; then
    "$PYTHON_BIN" -m pip install -r "$DIR/requirements.txt"
fi

exec "$PYTHON_BIN" "$DIR/run_pet.py" "$@"
""".replace("\r\n", "\n")

with open(os.path.join(macos_dir, "Desktop Pet"), "w", encoding="utf-8", newline="\n") as f:
    f.write(mac_exec_content)

# 3. launch.sh script for terminal / double-click
launch_sh_content = """#!/usr/bin/env bash
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
""".replace("\r\n", "\n")

with open(os.path.join(BASE_DIR, "launch.sh"), "w", encoding="utf-8", newline="\n") as f:
    f.write(launch_sh_content)

# 4. run_pet.py
run_pet_content = """#!/usr/bin/env python3
\"\"\"
Desktop Pet Griffin - macOS Edition (MacBook Air M1 / Apple Silicon)
Main execution entry point.
\"\"\"
import os
import sys

# Ensure current directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import run

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Desktop Pet Griffin (macOS Edition)")
    parser.add_argument("--style", choices=["cute", "real"], default=None, help="Start with cute or real griffin")
    parser.add_argument("--size", type=int, default=112, help="Pet size in pixels (default: 112)")
    parser.add_argument("--bed", action="store_true", help="Spawn permanent bed")
    parser.add_argument("--bowl", action="store_true", help="Spawn permanent food bowl")
    args, unknown = parser.parse_known_args()
    sys.exit(run(style=args.style, size=args.size, bed=args.bed, bowl=args.bowl))
""".replace("\r\n", "\n")

with open(os.path.join(BASE_DIR, "run_pet.py"), "w", encoding="utf-8", newline="\n") as f:
    f.write(run_pet_content)

print("Mac bundle, launch.sh, and run_pet.py successfully written with LF line endings!")
