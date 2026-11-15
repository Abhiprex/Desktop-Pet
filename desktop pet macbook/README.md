# Griffin Desktop Pet (v4 — Choose Your Griffin)

## 🦅 How to run
- Double-click **`Cozy Desktop Pet.exe`** (after rebuilding it, see below).
- A window asks **"Which Griffin would you like to see?"** — pick:
  - **Cute Griffin**: chibi baby griffin with big sparkly eyes, tiny beak, fluffy wings and a pom-pom tail.
  - **Real Griffin**: a majestic, realistic griffin — white eagle head with a hooked golden beak and fierce amber eye, lion body, big tawny wings, golden talons.
- You can switch any time: **right-click the pet → Switch Griffin**.

## 🐾 Behaviours (both griffins)
IDLE, WALK, PLAY, SLEEP, EAT and JUMP, each with 4 animation frames.
- Cute: hovers/flies, naps on a cloud, eats a star cookie.
- Real: stands proudly, strides on the ground with folded wings, screeches with flared wings, sleeps lying down, tears at a piece of meat, and leaps into flight with a wing upstroke.
- Drag it around, throw it, spawn a toy ball it will chase (right-click → Spawn Toy Ball), or turn on **Continuous Flying Mode** (right-click → Fly Around Screen 🦅) to let it soar across your entire desktop.
- **Permanent Desktop Items**:
  - **Cozy Pet Bed 🛏️**: Keeps a plush oval pet bed with soft cushion and headrest permanently on screen. Drag it anywhere or double-click / right-click pet to nap in bed.
  - **Snack Food Bowl 🥣**: Keeps a cute ceramic bowl with golden star biscuits and berries on screen. Drag it anywhere or double-click to feed your pet.
  - Toggle or disable them at any time by **right-clicking the pet** or the **system tray icon** in the taskbar!

## 🎨 Regenerating the art
- `sprite_generator.py` — cute griffin, toy ball, pet bed, and food bowl (and shared helpers). `sprite_generator_real.py` — realistic griffin.
- `python sprite_generator.py` regenerates all PNGs in `sprites/cute/` and `sprites/real/`.
- Colors are defined at the top of each file, so recoloring is easy.

## 🔨 Rebuilding the .exe (Windows)
```
pip install pyinstaller PyQt6 Pillow numpy
pyinstaller --noconsole --onefile --icon pet.ico --name "Cozy Desktop Pet" --add-data "sprites;sprites" main.py
```
The new exe appears in `dist/`. The `--add-data "sprites;sprites"` part includes both griffin folders.

## ✅ Tests
Run all unit and end-to-end tests:
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```
**41 tests passing** (assets, multi-res icon, physics, drag/drop bounds, gravity falling for toys/bed/bowl, autonomous navigation to bed/bowl, fuzzing, GUI widgets, both griffin styles, continuous 2D flight, permanent bed & food bowl widgets, and interactive toys).
