# 🐾 Desktop Pet Griffin — macOS Edition (MacBook Air M1)

A cozy, fully-interactive animated desktop griffin companion built with **Python & PyQt6**, natively optimized for **MacBook Air M1 (Apple Silicon `arm64`)** and macOS (Big Sur, Monterey, Ventura, Sonoma, and Sequoia).

---

## 🌟 Features on macOS
- **Native Apple Silicon M1 Support**: Runs at native `arm64` speed with zero emulation overhead and ultra-low battery consumption.
- **Retina Display Crisp Pixel Art**: Rendered with nearest-neighbor scaling for authentic, razor-sharp 16-bit retro aesthetics on MacBook Air's Retina display.
- **Dock & Menu Bar Aware**: Automatically detects your macOS Menu Bar at the top and the macOS Dock (whether at the bottom, left, or right), so the Griffin walks along the top edge of your Dock and flies beneath your Menu Bar.
- **Stays on Top Without Stealing Focus**: Floats above your desktop, Safari, VS Code, or terminal without interrupting your typing.
- **Mac Trackpad Optimized**: Full support for tap-to-click, two-finger secondary click (context menu), double-tap, and inertial flick-throwing physics.
- **Status Bar Menu (Tray Icon)**: Includes a companion icon in the top-right macOS Status Bar for quick actions and style switching.

---

## 🚀 Quick Start (MacBook Air M1)

### 1. Prerequisites
MacBook Air M1 comes with macOS. You will need Python 3 (3.9, 3.10, 3.11, 3.12, 3.13, or 3.14):

If you don't already have Python 3 installed, install it via [Homebrew](https://brew.sh/):
```bash
brew install python
```
*(Or download the official macOS installer from [python.org](https://www.python.org/downloads/macos/))*

### 2. Install Dependencies
Open **Terminal**, navigate to the project directory, and run:
```bash
cd "desktop pet macbook"
pip3 install -r requirements.txt
```

---

## 🎮 How to Launch

You have three easy ways to run the pet on macOS:

### Option A: Double-Click the App (Recommended)
Double-click **`Desktop Pet.app`** directly in Finder.
> **Note on macOS Gatekeeper**: The first time you launch on Mac, if prompted about an unsigned application:
> 1. Right-click (or Two-finger tap) on `Desktop Pet.app`.
> 2. Select **Open**.
> 3. Click **Open** in the confirmation dialog.

### Option B: Quick Terminal Launcher Script
In Terminal, run:
```bash
chmod +x launch.sh
./launch.sh
```
This automatically verifies Python 3, checks dependencies, and starts the pet.

### Option C: Direct Python Command
```bash
python3 run_pet.py
```

#### Optional Command-Line Flags
- `python3 run_pet.py --style cute` : Launch directly into Cute Griffin mode.
- `python3 run_pet.py --style real` : Launch directly into Real Griffin mode.
- `python3 run_pet.py --bed`        : Start with the cozy pet bed permanently on screen.
- `python3 run_pet.py --bowl`       : Start with the snack food bowl permanently on screen.
- `python3 run_pet.py --size 144`   : Customize size (80 = Small, 112 = Medium, 144 = Large).

---

## 🕹️ Trackpad & Mouse Controls

| Action | Trackpad Gesture | Effect |
| :--- | :--- | :--- |
| **Pick Up & Toss** | Click + Drag | Grabs the griffin. Release while moving to fling it across your screen with realistic gravity and bouncy landings! |
| **Context Menu** | Two-Finger Tap (Right-Click) | Opens the full menu (Switch Griffin, Walk, Fly, Star Cookie, Bed, Bowl, Size, Exit). |
| **Play with Toy Ball** | Click / Double-Click Ball | Bounces the beach ball into the air; your griffin will sprint or swoop to catch it! |
| **Nap in Bed** | Double-Click the Bed | The griffin walks to its cozy pillow bed, settles in front, and takes a restorative nap. |
| **Eat from Bowl** | Double-Click the Bowl | The griffin walks to the snack bowl and happily nibbles its kibbles. |
| **Startle Reaction** | Drag Bed or Bowl away | Moving furniture while the griffin is using it startles the pet into an alert hop and initiates an active chase! |

---

## 📁 Project Structure (macOS)

```text
desktop pet macbook/
├── Desktop Pet.app/            # Native macOS Application Bundle
│   └── Contents/
│       ├── Info.plist          # App bundle metadata & Retina high-res capability
│       ├── PkgInfo             # APPL signature
│       ├── MacOS/Desktop Pet   # Executable launcher script
│       └── Resources/pet.icns  # Multi-resolution Apple Icon Image
├── launch.sh                   # POSIX shell launcher for macOS Terminal
├── run_pet.py                  # Primary Python executable entrypoint
├── main.py                     # PyQt6 GUI & macOS Cocoa window management
├── pet_engine.py               # Pure-python physics simulation & state engine
├── pet.icns                    # macOS Apple Icon Image (16x16 to 1024x1024)
├── pet.ico                     # Multi-resolution ICO fallback
├── requirements.txt            # PyQt6 and Pillow dependencies
├── sprites/                    # 128x128 retro pixel art sprite sheets
│   ├── cute/                   # Cute Griffin ("Pip") complete animations
│   └── real/                   # Real Griffin complete animations
└── tests/                      # 45 automated unit and end-to-end test cases
    ├── test_pet.py
    └── test_e2e_comprehensive.py
```

---

## 🧪 Running Automated Tests on macOS
To run the full suite of 45 unit and end-to-end tests:
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
*(All 45 tests run cleanly offscreen with zero GUI display requirement).*
