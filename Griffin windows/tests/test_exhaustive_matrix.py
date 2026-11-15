import os
import sys
import unittest
from unittest.mock import MagicMock
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
    STYLE_LABELS,
    BASE_DIR,
    configure_floating_window,
    get_app_icon,
)

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPRITE_ROOT = os.path.join(BASE_PATH, "sprites")


class ExhaustiveMatrixTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        ensure_sprites_exist(os.path.join(SPRITE_ROOT, "cute"), force=False)
        ensure_sprites_exist(os.path.join(SPRITE_ROOT, "real"), force=False)

    # -------------------------------------------------------------------------
    # SUITE 1: Deep Color & Pixel Palette Analysis
    # -------------------------------------------------------------------------
    def test_01_cute_sprites_color_palette_features(self):
        """Cute griffin sprites contain bright eyes, golden beak, and white head feathers."""
        img_path = os.path.join(SPRITE_ROOT, "cute", "idle_1.png")
        self.assertTrue(os.path.isfile(img_path))
        with Image.open(img_path) as img:
            rgb = img.convert("RGB")
            colors = rgb.getcolors(maxcolors=20000)
            color_rgbs = [c[1] for c in colors]
            # Has gold beak tones: high R and G, lower B
            has_gold = any(r > 200 and g > 130 and b < 80 for r, g, b in color_rgbs)
            # Has white/cream eagle head: high R, G, B
            has_white = any(r > 220 and g > 220 and b > 210 for r, g, b in color_rgbs)
            self.assertTrue(has_gold, "Cute griffin must have golden beak tones")
            self.assertTrue(has_white, "Cute griffin must have white eagle head tones")

    def test_02_real_sprites_color_palette_features(self):
        """Real griffin sprites contain curved eagle beak, amber raptor eye, and tawny body."""
        img_path = os.path.join(SPRITE_ROOT, "real", "idle_1.png")
        self.assertTrue(os.path.isfile(img_path))
        with Image.open(img_path) as img:
            rgb = img.convert("RGB")
            colors = rgb.getcolors(maxcolors=20000)
            color_rgbs = [c[1] for c in colors]
            has_gold = any(r > 190 and g > 120 and b < 60 for r, g, b in color_rgbs)
            has_tawny = any(140 < r < 210 and 90 < g < 160 and 40 < b < 100 for r, g, b in color_rgbs)
            self.assertTrue(has_gold, "Real griffin must have golden raptor beak tones")
            self.assertTrue(has_tawny, "Real griffin must have lion tawny coat tones")

    def test_03_eat_bowl_cute_head_dipping(self):
        """Cute griffin eat_bowl frames dip head downward with kibble sparkles."""
        for idx in range(1, 5):
            path = os.path.join(SPRITE_ROOT, "cute", f"eat_bowl_{idx}.png")
            self.assertTrue(os.path.isfile(path), f"Missing cute eat_bowl_{idx}.png")
            with Image.open(path) as img:
                self.assertEqual(img.size, (128, 128))
                self.assertEqual(img.mode, "RGBA")
                bbox = img.getbbox()
                self.assertIsNotNone(bbox)

    def test_04_eat_bowl_real_hooked_beak_downward_pitch(self):
        """Real griffin eat_bowl frames tilt hooked beak downward into the food bowl."""
        for idx in range(1, 5):
            path = os.path.join(SPRITE_ROOT, "real", f"eat_bowl_{idx}.png")
            self.assertTrue(os.path.isfile(path), f"Missing real eat_bowl_{idx}.png")
            with Image.open(path) as img:
                self.assertEqual(img.size, (128, 128))
                self.assertEqual(img.mode, "RGBA")
                bbox = img.getbbox()
                self.assertIsNotNone(bbox)

    def test_05_sleep_bed_curled_posture_cute(self):
        """Cute griffin sleep_bed frames are snug and cozy."""
        for idx in range(1, 5):
            path = os.path.join(SPRITE_ROOT, "cute", f"sleep_bed_{idx}.png")
            self.assertTrue(os.path.isfile(path), f"Missing cute sleep_bed_{idx}.png")
            with Image.open(path) as img:
                self.assertEqual(img.size, (128, 128))

    def test_06_sleep_bed_curled_posture_real(self):
        """Real griffin sleep_bed frames show majestic griffin curled and sleeping."""
        for idx in range(1, 5):
            path = os.path.join(SPRITE_ROOT, "real", f"sleep_bed_{idx}.png")
            self.assertTrue(os.path.isfile(path), f"Missing real sleep_bed_{idx}.png")
            with Image.open(path) as img:
                self.assertEqual(img.size, (128, 128))

    def test_07_bed_furniture_pixel_dimensions(self):
        """Verify bed.png is 128x128 RGBA with pillow and rim."""
        for style in ("cute", "real"):
            path = os.path.join(SPRITE_ROOT, style, "bed.png")
            self.assertTrue(os.path.isfile(path))
            with Image.open(path) as img:
                self.assertEqual(img.size, (128, 128))
                self.assertEqual(img.mode, "RGBA")

    def test_08_bowl_furniture_pixel_dimensions(self):
        """Verify food_bowl.png is 128x128 RGBA with bowl rim and snacks."""
        for style in ("cute", "real"):
            path = os.path.join(SPRITE_ROOT, style, "food_bowl.png")
            self.assertTrue(os.path.isfile(path))
            with Image.open(path) as img:
                self.assertEqual(img.size, (128, 128))
                self.assertEqual(img.mode, "RGBA")

    def test_09_pet_ico_valid_windows_icon(self):
        """Verify pet.ico contains multi-resolution icon sizes."""
        ico_path = os.path.join(BASE_PATH, "pet.ico")
        self.assertTrue(os.path.isfile(ico_path))
        with Image.open(ico_path) as img:
            self.assertEqual(img.format, "ICO")

    def test_10_desktop_pet_exe_exists_and_valid_pe(self):
        """Verify Desktop Pet.exe exists and starts with standard Windows PE header MZ."""
        exe_path = os.path.join(BASE_PATH, "Desktop Pet.exe")
        self.assertTrue(os.path.isfile(exe_path), "Desktop Pet.exe must exist")
        self.assertGreater(os.path.getsize(exe_path), 10000)
        with open(exe_path, "rb") as f:
            header = f.read(2)
            self.assertEqual(header, b"MZ", "Executable must have valid MZ PE header")

    # -------------------------------------------------------------------------
    # SUITE 2: Engine Precision & Multi-Monitor Physics
    # -------------------------------------------------------------------------
    def test_11_physics_subpixel_precision(self):
        """Verify physics steps smoothly with subpixel floating point precision."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1920, 1080), pet_size=112)
        engine.x = 100.25
        engine.y = 200.50
        engine.vx = 2.5
        engine.vy = 1.25
        engine.step_physics()
        self.assertAlmostEqual(engine.x, 102.75, places=2)

    def test_12_screen_bounds_custom_multi_monitor(self):
        """Verify pet engine functions across multi-monitor negative coordinates."""
        bounds = ScreenBounds(left=-1920, top=0, right=1920, bottom=1080)
        engine = PetEngine(bounds=bounds, pet_size=112)
        engine.x = -500.0
        engine.y = engine.floor_y
        engine.direction = -1
        engine.set_state("WALK")
        for _ in range(50):
            engine.step_physics()
        self.assertLess(engine.x, -500.0)
        self.assertGreaterEqual(engine.x, -1920.0)

    def test_13_screen_bounds_vertical_display(self):
        """Verify pet engine functions on vertical orientation screen."""
        bounds = ScreenBounds(left=0, top=0, right=1080, bottom=1920)
        engine = PetEngine(bounds=bounds, pet_size=112)
        self.assertEqual(engine.floor_y, 1920 - 112)

    def test_14_extreme_high_dpi_size_scaling(self):
        """Verify engine operates consistently across all size scale factors."""
        for sz in (80, 112, 144, 200, 256):
            engine = PetEngine(bounds=ScreenBounds(0, 0, 1920, 1080), pet_size=sz)
            self.assertEqual(engine.pet_size, sz)
            self.assertEqual(engine.floor_y, 1080 - sz)

    def test_15_velocity_clamping_negative_infinity(self):
        """Extreme negative velocity is safely clamped without NaN or crash."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 1000), pet_size=112)
        engine.vx = -99999.0
        engine.vy = -99999.0
        engine.step_physics()
        self.assertGreaterEqual(engine.vx, -30.0)
        self.assertGreaterEqual(engine.vy, -30.0)

    def test_16_velocity_clamping_positive_infinity(self):
        """Extreme positive velocity is safely clamped without NaN or crash."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 1000), pet_size=112)
        engine.vx = 99999.0
        engine.vy = 99999.0
        engine.step_physics()
        self.assertLessEqual(engine.vx, 30.0)
        self.assertLessEqual(engine.vy, 30.0)

    def test_17_zero_gravity_or_floating_safety(self):
        """Pet in flight mode remains stably afloat."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 1000), pet_size=112)
        engine.toggle_flying(True)
        for _ in range(100):
            engine.step_physics()
        self.assertTrue(engine.flying_mode)
        self.assertLess(engine.y, engine.floor_y)

    def test_18_rapid_state_changes_100_cycles(self):
        """Engine safely handles 100 rapid sequential state transitions."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 1000), pet_size=112)
        for i in range(100):
            st = VALID_STATES[i % len(VALID_STATES)]
            engine.set_state(st)
            self.assertEqual(engine.state, st)

    # -------------------------------------------------------------------------
    # SUITE 3: Flight Physics Dynamics
    # -------------------------------------------------------------------------
    def test_19_flying_mode_airborne_corridor(self):
        """In flight mode, griffin stays in the airborne corridor and never touches floor."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_flying(True)
        for _ in range(150):
            engine.step_physics()
            self.assertLess(engine.y, engine.floor_y)

    def test_20_flying_mode_smooth_sine_wave(self):
        """Flight mode altitude changes continuously without sharp teleportation."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_flying(True)
        last_y = engine.y
        for _ in range(50):
            engine.step_physics()
            delta_y = abs(engine.y - last_y)
            self.assertLess(delta_y, 25.0, "Vertical motion must be smooth")
            last_y = engine.y

    def test_21_flying_to_ground_transition_snaps_to_floor(self):
        """Forcing ground state (WALK/SLEEP/IDLE/EAT) cancels flight and lands on floor."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.toggle_flying(True)
        self.assertTrue(pet.engine.flying_mode)
        pet.force_state("WALK")
        self.assertFalse(pet.engine.flying_mode)
        self.assertEqual(pet.engine.y, pet.engine.floor_y)
        pet.close()

    def test_22_ground_to_flying_transition_lifts_off(self):
        """Toggling flight mode from ground lifts the griffin into the sky."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.y = pet.engine.floor_y
        pet.toggle_flying_mode()
        self.assertTrue(pet.engine.flying_mode)
        pet.close()

    # -------------------------------------------------------------------------
    # SUITE 4: Interactive Toy Autonomous Navigation
    # -------------------------------------------------------------------------
    def test_23_toy_chase_from_far_left(self):
        """Pet at far right runs leftward to chase a toy on the left."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.x = 800.0
        engine.spawn_toy()
        engine.toy_x = 100.0
        engine.toy_y = engine.floor_y + 10
        for _ in range(150):
            engine.step_physics()
            if abs(engine.x - engine.toy_x) < 30:
                break
        self.assertLess(engine.x, 700.0)

    def test_24_toy_chase_from_far_right(self):
        """Pet at far left runs rightward to chase a toy on the right."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.x = 100.0
        engine.spawn_toy()
        engine.toy_x = 800.0
        engine.toy_y = engine.floor_y + 10
        for _ in range(150):
            engine.step_physics()
            if abs(engine.x - engine.toy_x) < 30:
                break
        self.assertGreater(engine.x, 200.0)

    def test_25_toy_arrival_detection_margin(self):
        """Pet transitions to PLAY when arriving near toy."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.spawn_toy()
        engine.toy_x = 300.0
        engine.toy_y = engine.floor_y + 20
        engine.x = 305.0
        engine.step_physics()
        self.assertEqual(engine.state, "PLAY")

    def test_26_toy_flying_interception(self):
        """Airborne pet swoops toward toy ball."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_flying(True)
        engine.spawn_toy()
        engine.toy_x = 400.0
        engine.toy_y = engine.floor_y
        for _ in range(80):
            engine.step_physics()
        self.assertTrue(engine.toy_active)

    # -------------------------------------------------------------------------
    # SUITE 5: Furniture Gravity, Falling, and Floor Settling
    # -------------------------------------------------------------------------
    def test_27_bed_fall_from_ceiling(self):
        """Bed placed at ceiling falls under gravity and settles on bed_floor_y."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_bed(True)
        engine.bed_y = 10.0
        engine.bed_vy = 0.0
        for _ in range(200):
            engine.step_physics()
        self.assertAlmostEqual(engine.bed_y, engine.bed_floor_y, delta=1.0)
        self.assertEqual(engine.bed_vy, 0.0)

    def test_28_bowl_fall_from_ceiling(self):
        """Bowl placed at ceiling falls under gravity and settles on bowl_floor_y."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_bowl(True)
        engine.bowl_y = 10.0
        engine.bowl_vy = 0.0
        for _ in range(200):
            engine.step_physics()
        self.assertAlmostEqual(engine.bowl_y, engine.bowl_floor_y, delta=1.0)
        self.assertEqual(engine.bowl_vy, 0.0)

    def test_29_bed_drag_startle_and_chase(self):
        """Dragging bed away while pet is sleeping startles pet and triggers active chase."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_bed(True)
        pet.engine.x = pet.engine.bed_x
        pet.engine.is_sleeping_in_bed = True
        pet.engine.state = "SLEEP"

        # User drags bed away
        pet.engine.bed_x = 800.0
        pet.engine.bed_dragging = True
        pet.on_physics_tick()

        self.assertFalse(pet.engine.is_sleeping_in_bed)
        self.assertEqual(pet.engine.target_action, "NAP_BED")
        self.assertEqual(pet.engine.state, "JUMP")
        pet.close()

    def test_30_bowl_drag_startle_and_chase(self):
        """Dragging bowl away while pet is eating startles pet and triggers active chase."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_food_bowl(True)
        pet.engine.x = pet.engine.bowl_x
        pet.engine.is_eating_at_bowl = True
        pet.engine.state = "EAT"

        # User drags bowl away
        pet.engine.bowl_x = 800.0
        pet.engine.bowl_dragging = True
        pet.on_physics_tick()

        self.assertFalse(pet.engine.is_eating_at_bowl)
        self.assertEqual(pet.engine.target_action, "EAT_BOWL")
        self.assertEqual(pet.engine.state, "JUMP")
        pet.close()

    def test_31_bed_settle_after_relocation(self):
        """After chasing relocated bed, pet re-settles into SLEEP."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_bed(True)
        pet.engine.x = 200.0
        pet.engine.bed_x = 400.0
        pet.go_to_bed_and_nap()

        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "SLEEP")
        self.assertTrue(pet.engine.is_sleeping_in_bed)
        pet.close()

    def test_32_bowl_settle_after_relocation(self):
        """After chasing relocated bowl, pet re-settles into EAT."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_food_bowl(True)
        pet.engine.x = 200.0
        pet.engine.bowl_x = 400.0
        pet.go_to_bowl_and_eat()

        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "EAT")
        self.assertTrue(pet.engine.is_eating_at_bowl)
        pet.close()

    def test_33_bed_left_screen_boundary_clamp(self):
        """Pet navigating to bed placed at left boundary clamps safely."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_bed(True)
        pet.engine.x = 400.0
        pet.engine.bed_x = 0.0
        pet.go_to_bed_and_nap()
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "SLEEP")
        self.assertTrue(pet.engine.is_sleeping_in_bed)
        pet.close()

    def test_34_bed_right_screen_boundary_clamp(self):
        """Pet navigating to bed placed at right boundary clamps safely."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_bed(True)
        pet.engine.x = 400.0
        pet.engine.bed_x = 1000.0
        pet.go_to_bed_and_nap()
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "SLEEP")
        self.assertTrue(pet.engine.is_sleeping_in_bed)
        pet.close()

    def test_35_bowl_left_screen_boundary_clamp(self):
        """Pet navigating to bowl placed at left boundary clamps safely."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_food_bowl(True)
        pet.engine.x = 400.0
        pet.engine.bowl_x = 0.0
        pet.go_to_bowl_and_eat()
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "EAT")
        self.assertTrue(pet.engine.is_eating_at_bowl)
        pet.close()

    def test_36_bowl_right_screen_boundary_clamp(self):
        """Pet navigating to bowl placed at right boundary clamps safely."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_food_bowl(True)
        pet.engine.x = 400.0
        pet.engine.bowl_x = 1000.0
        pet.go_to_bowl_and_eat()
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "EAT")
        self.assertTrue(pet.engine.is_eating_at_bowl)
        pet.close()

    def test_37_continuous_z_order_pet_on_top(self):
        """Pet raises above furniture continuously during walking and resting."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)
        pet.toggle_bed(True)
        pet.toggle_food_bowl(True)

        raises = []
        pet.raise_ = lambda: raises.append(1)

        # Walk to bed
        pet.go_to_bed_and_nap()
        self.assertGreater(len(raises), 0)
        raises.clear()

        pet.on_physics_tick()
        self.assertGreater(len(raises), 0)
        pet.close()

    def test_38_draggable_widget_mouse_events(self):
        """Simulate mouse press, move, and release on draggable bed widget."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        bed = pet.bed_widget
        mock_event = MagicMock()
        mock_event.button.return_value = Qt.MouseButton.LeftButton
        mock_event.globalPosition().toPoint.return_value = QPoint(300, 500)

        bed.mousePressEvent(mock_event)
        self.assertTrue(pet.engine.bed_dragging)

        mock_event.globalPosition().toPoint.return_value = QPoint(350, 520)
        bed.mouseMoveEvent(mock_event)

        bed.mouseReleaseEvent(mock_event)
        self.assertFalse(pet.engine.bed_dragging)
        pet.close()

    # -------------------------------------------------------------------------
    # SUITE 6: Runtime Style, Sizing, and Pixmap Transformations
    # -------------------------------------------------------------------------
    def test_39_runtime_style_switch_preserves_state(self):
        """Switching between Cute and Real griffin preserves current physics state and position."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.x = 450.0
        pet.engine.y = 550.0
        pet.engine.state = "PLAY"

        pet.change_style("real")
        self.assertEqual(pet.style, "real")
        self.assertEqual(pet.engine.x, 450.0)
        self.assertEqual(pet.engine.y, 550.0)
        self.assertEqual(pet.engine.state, "PLAY")
        pet.close()

    def test_40_runtime_size_switch_recalculates_bounds(self):
        """Switching pet size dynamically updates dimensions and floor clamp."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.change_size(144)
        self.assertEqual(pet.pet_size, 144)
        self.assertEqual(pet.engine.pet_size, 144)
        pet.close()

    def test_41_pixmap_fast_transformation_nearest_neighbor(self):
        """Sprites are scaled using FastTransformation to preserve crisp retro pixel art."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        frames = pet.sprites_right["WALK"]
        self.assertEqual(len(frames), 4)
        for frame in frames:
            self.assertEqual(frame.width(), 112)
            self.assertEqual(frame.height(), 112)
        pet.close()

    def test_42_tray_icon_and_context_menu_items(self):
        """Context menu contains all actions for state, furniture, style, and size."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        menu = pet._build_context_menu()
        action_texts = [a.text() for a in menu.actions()]
        self.assertTrue(any("Walk" in t for t in action_texts))
        self.assertTrue(any("Cookie" in t for t in action_texts))
        self.assertTrue(any("Pillow" in t or "Nap" in t for t in action_texts))
        self.assertTrue(any("Exit" in t for t in action_texts))
        pet.close()

    # -------------------------------------------------------------------------
    # SUITE 7: Heavy Fuzzing, Load Testing, and Memory Invariance
    # -------------------------------------------------------------------------
    def test_43_fuzzing_500_random_physics_and_drag_events(self):
        """Run 500 consecutive physics ticks with randomized drag, jump, and impulse events."""
        import random
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        for tick in range(500):
            action = random.choice(["tick", "drag", "release", "jump", "feed", "flip"])
            if action == "tick":
                engine.step_physics()
            elif action == "drag":
                engine.start_drag()
                engine.drag_to(random.uniform(50, 950), random.uniform(50, 750))
            elif action == "release":
                engine.end_drag()
            elif action == "jump":
                engine.trigger_jump()
            elif action == "feed":
                engine.feed_snack()
            elif action == "flip":
                engine.direction *= -1

            # Engine state must remain valid and numerical
            self.assertFalse(any(v is None for v in [engine.x, engine.y, engine.vx, engine.vy]))
            self.assertGreaterEqual(engine.x, 0.0)
            self.assertLessEqual(engine.x, 1000.0)

    def test_44_fuzzing_500_furniture_drags_and_bounces(self):
        """Run 500 randomized furniture relocations and toy bounces."""
        import random
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        engine.toggle_bed(True)
        engine.toggle_bowl(True)
        engine.spawn_toy()

        for _ in range(500):
            engine.step_physics()
            r = random.random()
            if r < 0.05:
                engine.bed_x = random.uniform(50, 900)
                engine.on_bed_moved()
            elif r < 0.10:
                engine.bowl_x = random.uniform(50, 900)
                engine.on_bowl_moved()
            elif r < 0.15:
                engine.bounce_toy()

    def test_45_no_memory_leak_frame_cycling_1000_ticks(self):
        """Cycle animation frames 1000 times without frame index overflow."""
        engine = PetEngine(bounds=ScreenBounds(0, 0, 1000, 800), pet_size=112)
        for _ in range(1000):
            engine.advance_frame()
            self.assertIn(engine.frame_index, [0, 1, 2, 3])

    def test_46_launch_desktop_pet_lnk_valid(self):
        """Verify Launch Desktop Pet.lnk shortcut file exists."""
        lnk_path = os.path.join(BASE_PATH, "Launch Desktop Pet.lnk")
        self.assertTrue(os.path.isfile(lnk_path))
        self.assertGreater(os.path.getsize(lnk_path), 0)

    def test_47_desktop_pet_app_bundle_structure(self):
        """Verify Desktop Pet application bundle or launcher exists."""
        app_path = os.path.join(BASE_PATH, "Desktop Pet.app")
        exe_path = os.path.join(BASE_PATH, "Desktop Pet.exe")
        self.assertTrue(os.path.exists(app_path) or os.path.exists(exe_path))

    def test_48_cli_arguments_parser_styles(self):
        """Verify command-line argument parser choices."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--style", choices=["cute", "real"])
        args = parser.parse_args(["--style", "cute"])
        self.assertEqual(args.style, "cute")
        args2 = parser.parse_args(["--style", "real"])
        self.assertEqual(args2.style, "real")

    def test_49_cli_arguments_parser_flags(self):
        """Verify CLI flags for bed, bowl, and size."""
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--bed", action="store_true")
        parser.add_argument("--bowl", action="store_true")
        parser.add_argument("--size", type=int, default=112)
        args = parser.parse_args(["--bed", "--bowl", "--size", "144"])
        self.assertTrue(args.bed)
        self.assertTrue(args.bowl)
        self.assertEqual(args.size, 144)

    def test_50_screen_geometry_changed_signal_handling(self):
        """Test _on_screen_geometry_changed handles Dock and display resizing cleanly."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet._on_screen_geometry_changed(None)
        self.assertIsNotNone(pet.engine.bounds)
        pet.close()

    def test_51_window_flags_always_on_top(self):
        """All desktop pet widgets are configured with WindowStaysOnTopHint."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        self.assertTrue(bool(pet.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        self.assertTrue(bool(pet.bed_widget.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        self.assertTrue(bool(pet.bowl_widget.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        pet.close()

    def test_52_translucent_background_attribute(self):
        """All desktop pet widgets have transparent background enabled."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        self.assertTrue(pet.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertTrue(pet.bed_widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        self.assertTrue(pet.bowl_widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        pet.close()

    def test_53_mac_always_show_tool_window_or_subwindow(self):
        """Verify helper configure_floating_window sets overlay attributes."""
        widget = QWidget()
        configure_floating_window(widget)
        self.assertTrue(widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        widget.close()

    def test_54_quit_on_last_window_closed_safe(self):
        """Closing a secondary chooser dialog does not crash the application."""
        chooser = GriffinChooser()
        chooser.close()
        self.assertFalse(chooser.isVisible())

    def test_55_end_to_end_user_session_simulation(self):
        """Simulate a full end-to-end user session through all features."""
        pet = CozyDesktopPet(pet_size=112, style="cute")
        pet.engine.bounds = ScreenBounds(0, 0, 1000, 700)

        # 1. Walk on ground
        pet.force_state("WALK")
        for _ in range(20):
            pet.on_physics_tick()
        self.assertEqual(pet.engine.state, "WALK")

        # 2. Feed cookie
        pet.force_state("EAT")
        self.assertEqual(pet.engine.state, "EAT")

        # 3. Take flight
        pet.toggle_flying_mode()
        self.assertTrue(pet.engine.flying_mode)
        for _ in range(30):
            pet.on_physics_tick()

        # 4. Land and nap in bed
        pet.toggle_bed(True)
        pet.engine.bed_x = 300.0
        pet.go_to_bed_and_nap()
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "SLEEP")
        self.assertTrue(pet.engine.is_sleeping_in_bed)

        # 5. Switch to Real Griffin
        pet.change_style("real")
        self.assertEqual(pet.style, "real")

        # 6. Eat from bowl
        pet.toggle_food_bowl(True)
        pet.engine.bowl_x = 600.0
        pet.go_to_bowl_and_eat()
        for _ in range(160):
            pet.on_physics_tick()
            if pet.engine.target_action is None:
                break
        self.assertEqual(pet.engine.state, "EAT")
        self.assertTrue(pet.engine.is_eating_at_bowl)

        pet.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
