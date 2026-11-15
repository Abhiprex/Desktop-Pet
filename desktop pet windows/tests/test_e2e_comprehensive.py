import os
import sys
import unittest
from unittest.mock import MagicMock
from PIL import Image
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pet_engine import PetEngine, ScreenBounds, VALID_STATES
from sprite_generator import ensure_sprites_exist
from main import CozyDesktopPet, GriffinChooser, STYLE_LABELS, BASE_DIR

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPRITE_ROOT = os.path.join(BASE_PATH, "sprites")


class ComprehensiveProjectE2ETest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        ensure_sprites_exist(os.path.join(SPRITE_ROOT, "cute"), force=False)
        ensure_sprites_exist(os.path.join(SPRITE_ROOT, "real"), force=False)

    def test_01_all_50_sprites_valid_and_non_empty(self):
        """Verify all 25 cute sprites and 25 real sprites exist, 128x128 RGBA, non-empty."""
        expected_names = ["toy.png"] + [f"{s.lower()}_{i}.png" for s in VALID_STATES for i in range(1, 5)]
        self.assertEqual(len(expected_names), 25)

        for style in ("cute", "real"):
            style_dir = os.path.join(SPRITE_ROOT, style)
            for fname in expected_names:
                fpath = os.path.join(style_dir, fname)
                self.assertTrue(os.path.isfile(fpath), f"Missing asset: {fpath}")
                with Image.open(fpath) as img:
                    self.assertEqual(img.size, (128, 128))
                    self.assertEqual(img.mode, "RGBA")
                    bbox = img.getbbox()
                    self.assertIsNotNone(bbox, f"Asset is completely blank: {fpath}")
                    # Ensure bounding box has substantial area
                    self.assertGreater(bbox[2] - bbox[0], 20)
                    self.assertGreater(bbox[3] - bbox[1], 20)

    def test_02_pet_icon_multi_resolution(self):
        """Verify pet.ico exists and has full multi-resolution icon sizes."""
        ico_path = os.path.join(BASE_PATH, "pet.ico")
        self.assertTrue(os.path.isfile(ico_path))
        with Image.open(ico_path) as img:
            self.assertEqual(img.format, "ICO")
            sizes = getattr(img, "ico", None).sizes()
            for required_size in ((16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)):
                self.assertIn(required_size, sizes)

    def test_03_launchers_and_entrypoints_exist(self):
        """Verify all launchers and entry point scripts exist and have content."""
        launchers = [
            "main.py",
            "run_pet.pyw",
            "Launch Desktop Pet.lnk",
            "Launch Desktop Pet.bat",
            "Launch Desktop Pet.vbs",
            "create_shortcuts.py",
        ]
        for name in launchers:
            path = os.path.join(BASE_PATH, name)
            self.assertTrue(os.path.isfile(path), f"Missing launcher/script: {name}")
            self.assertGreater(os.path.getsize(path), 0, f"Empty file: {name}")

    def test_04_flight_mode_locks_flying_animation_in_air(self):
        """Verify flying mode continuously maintains JUMP flight animation and stays aloft."""
        bounds = ScreenBounds(left=0, top=0, right=1920, bottom=1080)
        engine = PetEngine(bounds=bounds, pet_size=112)
        
        # Ground mode initially
        self.assertFalse(engine.flying_mode)
        self.assertEqual(engine.y, engine.floor_y)
        
        # Turn ON flying mode
        engine.toggle_flying(True)
        self.assertTrue(engine.flying_mode)
        self.assertEqual(engine.state, "JUMP")

        # Step 150 physics ticks: pet must stay aloft and remain in JUMP flight state
        for _ in range(150):
            engine.step_physics()
            self.assertEqual(engine.state, "JUMP")
            self.assertLess(engine.y, engine.floor_y)
            self.assertGreaterEqual(engine.y, float(bounds.top))
            self.assertGreaterEqual(engine.x, float(bounds.left))
            self.assertLessEqual(engine.x, float(bounds.right - engine.pet_size))

        # Test state decisions during flight: must never revert to WALK on thin air
        import random
        for _ in range(50):
            state = engine.pick_next_state(rng=random.Random(42))
            self.assertEqual(state, "JUMP")

    def test_05_ground_mode_locks_walking_to_taskbar_floor(self):
        """Verify ground mode walks strictly along the taskbar/floor edge."""
        bounds = ScreenBounds(left=0, top=0, right=1920, bottom=1080)
        engine = PetEngine(bounds=bounds, pet_size=112)
        
        # Explicit ground walking
        engine.set_state("WALK")
        self.assertFalse(engine.flying_mode)
        self.assertEqual(engine.y, engine.floor_y)

        # Step 100 physics ticks: pet must remain on floor_y
        for _ in range(100):
            engine.step_physics()
            self.assertEqual(engine.y, engine.floor_y)

    def test_06_gui_live_switching_and_flight_toggle(self):
        """Simulate real user interaction in the GUI widget across both griffin styles."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        self.assertEqual(pet.style, "cute")
        
        # Verify initial rendering
        pet.render_current_frame()
        self.assertFalse(pet.label.pixmap().isNull())

        # Toggle Flying Mode
        pet.toggle_flying_mode()
        self.assertTrue(pet.engine.flying_mode)
        for _ in range(25):
            pet.on_physics_tick()
            pet.on_animation_tick()
            self.assertEqual(pet.engine.state, "JUMP")
            self.assertLess(pet.engine.y, pet.engine.floor_y)

        # Switch Griffin to Real while in mid-air
        pet.change_style("real")
        self.assertEqual(pet.style, "real")
        self.assertTrue(pet.sprite_dir.endswith("real"))
        pet.render_current_frame()
        self.assertFalse(pet.label.pixmap().isNull())
        for _ in range(25):
            pet.on_physics_tick()
            pet.on_animation_tick()
            self.assertEqual(pet.engine.state, "JUMP")

        # Switch to Walk on Ground: must settle directly onto floor
        pet.force_state("WALK")
        self.assertFalse(pet.engine.flying_mode)
        self.assertEqual(pet.engine.y, pet.engine.floor_y)
        self.assertEqual(pet.engine.state, "WALK")
        for _ in range(25):
            pet.on_physics_tick()
            pet.on_animation_tick()
            self.assertEqual(pet.engine.y, pet.engine.floor_y)

        # Resize pet dynamically
        for sz in (80, 144, 112):
            pet.change_size(sz)
            self.assertEqual(pet.pet_size, sz)
            self.assertEqual(pet.engine.pet_size, sz)

    def test_07_interactive_toy_aerial_swoop_and_ground_play(self):
        """Test ball chasing both while flying in the air and while walking on the ground."""
        pet = CozyDesktopPet(pet_size=112)
        
        # Ground toy chasing
        pet.toggle_toy_ball()
        self.assertTrue(pet.engine.toy_active)
        self.assertTrue(pet.toy_widget.isVisible())
        for _ in range(60):
            pet.on_physics_tick()
        
        # Flying toy swoop
        pet.toggle_flying_mode()
        self.assertTrue(pet.engine.flying_mode)
        for _ in range(60):
            pet.on_physics_tick()
        self.assertEqual(pet.engine.state, "JUMP")

        # Dismiss toy ball
        pet.toggle_toy_ball()
        self.assertFalse(pet.engine.toy_active)

    def test_08_griffin_chooser_dialog_initialization(self):
        """Verify the GriffinChooser dialog initializes properly with card toolbuttons."""
        chooser = GriffinChooser()
        self.assertEqual(chooser.windowTitle(), "Choose your Griffin")
        self.assertIsNone(chooser.choice)

    def test_09_permanent_bed_and_food_bowl_sprites_and_widgets(self):
        """Verify bed.png and food_bowl.png assets exist, and draggable widgets toggle and drag."""
        for style in ("cute", "real"):
            for fname in ("bed.png", "food_bowl.png"):
                fpath = os.path.join(SPRITE_ROOT, style, fname)
                self.assertTrue(os.path.isfile(fpath), f"Missing {fpath}")
                with Image.open(fpath) as img:
                    self.assertEqual(img.size, (128, 128))
                    self.assertEqual(img.mode, "RGBA")
                    self.assertIsNotNone(img.getbbox())

        pet = CozyDesktopPet(pet_size=112)
        
        # Test Bed widget
        pet.toggle_bed(True)
        self.assertTrue(pet.bed_widget.isVisible())
        self.assertEqual(pet.bed_widget.width(), pet.engine.bed_size)
        pet.force_state("SLEEP")
        for _ in range(30):
            pet.on_physics_tick()
        pet.toggle_bed(False)
        self.assertFalse(pet.bed_widget.isVisible())

        # Test Food Bowl widget
        pet.toggle_food_bowl(True)
        self.assertTrue(pet.bowl_widget.isVisible())
        self.assertEqual(pet.bowl_widget.width(), pet.engine.bowl_size)
        pet.force_state("EAT")
        for _ in range(30):
            pet.on_physics_tick()
        pet.toggle_food_bowl(False)
        self.assertFalse(pet.bowl_widget.isVisible())

        # Close all helper widgets
        pet.close()

    def test_10_interactive_bed_and_bowl_displaced_reaction_and_sprites(self):
        """Verify new eat_bowl and sleep_bed sprites for both styles, and GUI displacement reactions."""
        # 1. Verify sprite files exist for both cute and real styles
        for style in ("cute", "real"):
            for prefix in ("eat_bowl", "sleep_bed"):
                for i in range(1, 5):
                    fpath = os.path.join(SPRITE_ROOT, style, f"{prefix}_{i}.png")
                    self.assertTrue(os.path.isfile(fpath), f"Missing {fpath}")
                    with Image.open(fpath) as img:
                        self.assertEqual(img.size, (128, 128))
                        self.assertEqual(img.mode, "RGBA")
                        self.assertIsNotNone(img.getbbox())

        # 2. Test GUI interactions and reactions with CozyDesktopPet
        pet = CozyDesktopPet(pet_size=112)
        pet.engine.x = 200.0
        pet.engine.y = pet.engine.floor_y

        # Toggle bowl and send pet to eat
        pet.toggle_food_bowl(True)
        pet.engine.bowl_x = 400.0
        pet.engine.bowl_y = pet.engine.bowl_floor_y
        pet.go_to_bowl_and_eat()
        self.assertEqual(pet.engine.target_action, "EAT_BOWL")

        for _ in range(80):
            pet.on_physics_tick()
        self.assertEqual(pet.engine.state, "EAT")
        self.assertTrue(pet.engine.is_eating_at_bowl)
        # Verify render frame doesn't crash and uses eat_bowl
        pet.render_current_frame()

        # Simulate user moving bowl while pet is eating!
        pet.engine.bowl_x = 750.0
        pet.engine.on_bowl_moved()
        self.assertFalse(pet.engine.is_eating_at_bowl)
        self.assertEqual(pet.engine.target_action, "EAT_BOWL")
        self.assertEqual(pet.engine.state, "JUMP")

        # Let pet chase and reach new bowl position
        for _ in range(120):
            pet.on_physics_tick()
        self.assertEqual(pet.engine.state, "EAT")
        self.assertTrue(pet.engine.is_eating_at_bowl)

        # Toggle bed and send pet to nap
        pet.toggle_bed(True)
        pet.engine.bed_x = 550.0
        pet.engine.bed_y = pet.engine.bed_floor_y
        pet.go_to_bed_and_nap()
        self.assertEqual(pet.engine.target_action, "NAP_BED")

        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "SLEEP")
        self.assertTrue(pet.engine.is_sleeping_in_bed)
        pet.render_current_frame()

        # Simulate user dragging bed away while pet is sleeping!
        pet.engine.bed_x = 800.0
        pet.engine.bed_dragging = True
        pet.on_physics_tick()
        self.assertFalse(pet.engine.is_sleeping_in_bed)
        self.assertEqual(pet.engine.target_action, "NAP_BED")
        self.assertEqual(pet.engine.state, "JUMP")

        # Release and let pet chase back and settle into bed
        pet.engine.bed_dragging = False
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "SLEEP")
        self.assertTrue(pet.engine.is_sleeping_in_bed)

        pet.close()

    def test_11_continuous_z_order_raises_pet_in_front_of_bed_and_bowl(self):
        """Verify the pet maintains continuous Z-order in front of bed and bowl without popping."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)

        raise_calls = []
        original_raise = pet.raise_
        pet.raise_ = lambda: raise_calls.append("raise")

        # 1. Toggling bed on should raise pet in front
        pet.toggle_bed(True)
        self.assertIn("raise", raise_calls)
        raise_calls.clear()

        # 2. Triggering go_to_bed_and_nap should immediately raise pet
        pet.engine.x = 100.0
        pet.engine.bed_x = 400.0
        pet.go_to_bed_and_nap()
        self.assertIn("raise", raise_calls)
        self.assertEqual(pet.engine.target_action, "NAP_BED")
        raise_calls.clear()

        # 3. During the walk, every tick should keep the pet in front (no jumping or popping behind)
        pet.on_physics_tick()
        self.assertIn("raise", raise_calls)
        self.assertEqual(pet.engine.target_action, "NAP_BED")
        raise_calls.clear()

        # 4. Releasing mouse drag on bed should raise pet
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton
        pet.engine.bed_dragging = True
        pet.bed_widget.mouseReleaseEvent(event)
        self.assertIn("raise", raise_calls)
        raise_calls.clear()

        # Restore
        pet.raise_ = original_raise
        pet.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
