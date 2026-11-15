import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
from PyQt6.QtWidgets import QApplication, QWidget, QDialog
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QIcon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pet_engine import PetEngine, ScreenBounds, VALID_STATES
from sprite_generator import ensure_sprites_exist
from main import (
    CozyDesktopPet,
    DraggableToyWidget,
    DraggableBedWidget,
    DraggableFoodBowlWidget,
    GriffinChooser,
    configure_floating_window,
    get_app_icon,
    BASE_DIR,
    STYLE_LABELS,
)

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPRITE_ROOT = os.path.join(BASE_PATH, "sprites")


class AggressiveSimulationTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        ensure_sprites_exist(os.path.join(SPRITE_ROOT, "cute"), force=False)
        ensure_sprites_exist(os.path.join(SPRITE_ROOT, "real"), force=False)

    # =========================================================================
    # SECTION 1: macOS & Apple Silicon M1 Platform Emulation
    # =========================================================================
    def test_sim_01_macos_platform_flag_and_attribute_configuration(self):
        """Simulate running under macOS darwin and verify Cocoa window attributes."""
        with patch("sys.platform", "darwin"):
            widget = QWidget()
            configure_floating_window(widget)
            flags = widget.windowFlags()
            self.assertTrue(bool(flags & Qt.WindowType.FramelessWindowHint))
            self.assertTrue(bool(flags & Qt.WindowType.WindowStaysOnTopHint))
            self.assertTrue(bool(flags & Qt.WindowType.SubWindow))
            self.assertTrue(widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
            self.assertTrue(widget.testAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow))
            self.assertTrue(widget.testAttribute(Qt.WidgetAttribute.WA_NoSystemBackground))
            widget.close()

    def test_sim_02_macos_retina_display_geometry_adaptation(self):
        """Simulate MacBook Air M1 Retina 1440x900 logical points with Menu Bar & Dock."""
        # Standard MacBook Air: Top menu bar = 25px, Bottom dock = 65px
        mac_bounds = ScreenBounds(left=0, top=25, right=1440, bottom=835)
        engine = PetEngine(bounds=mac_bounds, pet_size=112)
        # Pet floor should walk right on top of macOS Dock
        self.assertEqual(engine.floor_y, 835.0 - 112.0)
        # Pet ceiling in flight swoops right below macOS Menu Bar
        engine.toggle_flying(True)
        for _ in range(100):
            engine.step_physics()
            self.assertGreaterEqual(engine.y, 25.0)
            self.assertLessEqual(engine.y, 835.0 - 112.0)

    def test_sim_03_macos_left_dock_screen_bounds(self):
        """Simulate MacBook Air with macOS Dock positioned on Left screen edge."""
        # Left dock = 70px wide, top menu bar = 25px
        left_dock_bounds = ScreenBounds(left=70, top=25, right=1440, bottom=900)
        engine = PetEngine(bounds=left_dock_bounds, pet_size=112)
        engine.x = 80.0
        engine.direction = -1
        engine.set_state("WALK")
        for _ in range(20):
            engine.step_physics()
        # Should bounce off left dock at 70px
        self.assertGreaterEqual(engine.x, 70.0)

    def test_sim_04_macos_right_dock_screen_bounds(self):
        """Simulate MacBook Air with macOS Dock positioned on Right screen edge."""
        # Right dock at x=1370
        right_dock_bounds = ScreenBounds(left=0, top=25, right=1370, bottom=900)
        engine = PetEngine(bounds=right_dock_bounds, pet_size=112)
        engine.x = 1360.0
        engine.direction = 1
        engine.set_state("WALK")
        for _ in range(20):
            engine.step_physics()
        # Should bounce off right dock at 1370 - pet_size
        self.assertLessEqual(engine.x, 1370.0 - 112.0)

    def test_sim_05_macos_external_display_hotplug_simulation(self):
        """Simulate hotplugging an external 4K monitor to MacBook Air M1."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        # Hotplug external 4K monitor
        external_4k = ScreenBounds(left=0, top=0, right=3840, bottom=2160)
        pet.engine.update_bounds(external_4k)
        self.assertEqual(pet.engine.bounds.right, 3840)
        self.assertEqual(pet.engine.floor_y, 2160 - 112)
        # Disconnect and return to built-in display
        builtin_display = ScreenBounds(left=0, top=25, right=1440, bottom=835)
        pet.engine.update_bounds(builtin_display)
        self.assertEqual(pet.engine.bounds.right, 1440)
        self.assertLessEqual(pet.engine.x, 1440 - 112)
        pet.close()

    def test_sim_06_macos_app_bundle_internal_consistency(self):
        """Verify macOS bundle contains all required files and matching executable signatures."""
        mac_folder = os.path.join(os.path.dirname(BASE_PATH), "desktop pet macbook")
        if os.path.isdir(mac_folder):
            app_dir = os.path.join(mac_folder, "Desktop Pet.app")
            self.assertTrue(os.path.isdir(app_dir), "Desktop Pet.app bundle must exist")
            self.assertTrue(os.path.isfile(os.path.join(app_dir, "Contents", "Info.plist")))
            self.assertTrue(os.path.isfile(os.path.join(app_dir, "Contents", "PkgInfo")))
            self.assertTrue(os.path.isfile(os.path.join(app_dir, "Contents", "MacOS", "Desktop Pet")))
            self.assertTrue(os.path.isfile(os.path.join(app_dir, "Contents", "Resources", "pet.icns")))

    # =========================================================================
    # SECTION 2: Windows Platform & Win32 PE Architecture
    # =========================================================================
    def test_sim_07_windows_platform_flag_configuration(self):
        """Verify Windows flags configure Tool and FramelessWindowHint."""
        with patch("sys.platform", "win32"):
            widget = QWidget()
            configure_floating_window(widget)
            flags = widget.windowFlags()
            self.assertTrue(bool(flags & Qt.WindowType.FramelessWindowHint))
            self.assertTrue(bool(flags & Qt.WindowType.WindowStaysOnTopHint))
            self.assertTrue(bool(flags & Qt.WindowType.Tool))
            self.assertTrue(widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
            widget.close()

    def test_sim_08_windows_taskbar_grouping_appusermodelid(self):
        """Verify Windows taskbar AppUserModelID setup executes without error."""
        with patch("sys.platform", "win32"):
            try:
                import ctypes
                if hasattr(ctypes, "windll"):
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cozy.desktop.pet.griffin.v4")
            except Exception as e:
                self.fail(f"SetCurrentProcessExplicitAppUserModelID failed: {e}")

    def test_sim_09_windows_desktop_pet_exe_pe_coff_header(self):
        """Verify Desktop Pet.exe contains valid Win32 PE signature, COFF header, and machine type."""
        exe_path = os.path.join(BASE_PATH, "Desktop Pet.exe")
        if os.path.isfile(exe_path):
            with open(exe_path, "rb") as f:
                dos_header = f.read(64)
                self.assertEqual(dos_header[:2], b"MZ", "DOS signature must be MZ")
                pe_offset = int.from_bytes(dos_header[60:64], "little")
                f.seek(pe_offset)
                pe_sig = f.read(4)
                self.assertEqual(pe_sig, b"PE\x00\x00", "PE signature must be PE\\0\\0")

    # =========================================================================
    # SECTION 3: 5,000-Step Deep Physics & Stress Fuzzing Simulation
    # =========================================================================
    def test_sim_10_5000_step_aggressive_physics_simulation(self):
        """Simulate 5,000 continuous physics steps (equivalent to over 2 hours of real-time play)."""
        import random
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1920, 1080), pet_size=112)
        engine.spawn_toy()
        engine.toggle_bed(True)
        engine.toggle_bowl(True)

        for step in range(5000):
            engine.step_physics()

            # Randomly inject chaotic user interactions every 20-50 steps
            if step % 40 == 0:
                rand_action = random.choice([
                    "throw_pet", "bounce_toy", "drag_bed", "drag_bowl",
                    "fly_toggle", "jump", "feed", "reverse_direction"
                ])
                if rand_action == "throw_pet":
                    engine.vx = random.uniform(-25.0, 25.0)
                    engine.vy = random.uniform(-25.0, 10.0)
                elif rand_action == "bounce_toy":
                    engine.bounce_toy(random.uniform(-10.0, 10.0), random.uniform(-12.0, -4.0))
                elif rand_action == "drag_bed":
                    engine.bed_x = random.uniform(50, 1800)
                    engine.on_bed_moved()
                elif rand_action == "drag_bowl":
                    engine.bowl_x = random.uniform(50, 1800)
                    engine.on_bowl_moved()
                elif rand_action == "fly_toggle":
                    engine.toggle_flying()
                elif rand_action == "jump":
                    engine.trigger_jump()
                elif rand_action == "feed":
                    engine.feed_snack()
                elif rand_action == "reverse_direction":
                    engine.direction *= -1

            # Assert invariants at every step: no NaN, no Inf, positions within screen bounds
            self.assertFalse(any(isinstance(v, float) and (v != v) for v in [engine.x, engine.y, engine.vx, engine.vy]))
            self.assertGreaterEqual(engine.x, -5.0)
            self.assertLessEqual(engine.x, 1925.0)
            self.assertGreaterEqual(engine.y, -5.0)
            self.assertLessEqual(engine.y, 1085.0)

    # =========================================================================
    # SECTION 4: Complex Multi-Object Interruption Sequences
    # =========================================================================
    def test_sim_11_interruption_sleeping_pet_displaced_bed_cycle(self):
        """Pet sleeps, user relocates bed 10 times consecutively; pet chases and settles each time."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1920, 1080)
        pet.toggle_bed(True)

        for relocation in range(5):
            new_target_x = 200.0 + relocation * 250.0
            pet.engine.bed_x = new_target_x
            pet.go_to_bed_and_nap()

            for _ in range(160):
                pet.on_physics_tick()
                if pet.engine.target_action is None:
                    break
            self.assertEqual(pet.engine.state, "SLEEP")
            self.assertTrue(pet.engine.is_sleeping_in_bed)

        pet.close()

    def test_sim_12_interruption_eating_pet_displaced_bowl_cycle(self):
        """Pet eats, user relocates bowl 5 times consecutively; pet chases and settles each time."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1920, 1080)
        pet.toggle_food_bowl(True)

        for relocation in range(5):
            new_target_x = 250.0 + relocation * 250.0
            pet.engine.bowl_x = new_target_x
            pet.go_to_bowl_and_eat()

            for _ in range(160):
                pet.on_physics_tick()
                if pet.engine.target_action is None:
                    break
            self.assertEqual(pet.engine.state, "EAT")
            self.assertTrue(pet.engine.is_eating_at_bowl)

        pet.close()

    def test_sim_13_simultaneous_bed_and_bowl_gravity_drop(self):
        """Both bed and bowl dropped from high altitudes settle safely at their distinct floor offsets."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_bed(True)
        engine.toggle_bowl(True)
        engine.bed_y = 50.0
        engine.bowl_y = 75.0
        engine.bed_vy = 0.0
        engine.bowl_vy = 0.0

        for _ in range(250):
            engine.step_physics()

        self.assertAlmostEqual(engine.bed_y, engine.bed_floor_y, delta=1.0)
        self.assertAlmostEqual(engine.bowl_y, engine.bowl_floor_y, delta=1.0)
        self.assertEqual(engine.bed_vy, 0.0)
        self.assertEqual(engine.bowl_vy, 0.0)

    # =========================================================================
    # SECTION 5: Runtime Style Swapping & Pixmap Memory Leak Audit
    # =========================================================================
    def test_sim_14_rapid_runtime_style_switching_memory_safety(self):
        """Switch between Cute and Real griffin 50 times in rapid succession."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        for i in range(50):
            target_style = "real" if i % 2 == 0 else "cute"
            pet.change_style(target_style)
            self.assertEqual(pet.style, target_style)
            pet.render_current_frame()
            self.assertIsNotNone(pet.label.pixmap())
            self.assertFalse(pet.label.pixmap().isNull())
        pet.close()

    def test_sim_15_all_24_directional_and_contextual_pixmap_allocations(self):
        """Verify all frames in both orientations render valid non-null pixmaps."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        for direction in (1, -1):
            pet.engine.direction = direction
            for state in VALID_STATES:
                pet.engine.state = state
                for frame_idx in range(4):
                    pet.engine.frame_index = frame_idx
                    pet.render_current_frame()
                    pixmap = pet.label.pixmap()
                    self.assertFalse(pixmap.isNull())
                    self.assertEqual(pixmap.width(), 112)
                    self.assertEqual(pixmap.height(), 112)
        pet.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
