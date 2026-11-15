"""
Comprehensive Unit & Integration Test Suite for Puppy & Cat Desktop Pets.
Over 40 thorough test cases covering:
- Asset generation and pixel integrity
- Screen boundaries and physics simulation
- Furniture interaction, gravity, and settlement
- Dual pet state machines, autonomous navigation, and social AI
- Follow-cursor tracking and ball physics
- GUI widget initialization, menu signal signatures, and particle lifecycle
"""

import os
import sys
import unittest
from unittest.mock import MagicMock
from PIL import Image

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from pet_engine import FurnitureItem, MultiPetEngine, PetEntity, ScreenBounds, VALID_STATES


class TestPuppyCatAssets(unittest.TestCase):
    """1-12: Asset existence, dimensions, color modes, and icon structure."""

    def test_01_puppy_directory_exists(self):
        p_dir = os.path.join(PROJECT_ROOT, "sprites", "puppy")
        self.assertTrue(os.path.isdir(p_dir))

    def test_02_kitten_directory_exists(self):
        k_dir = os.path.join(PROJECT_ROOT, "sprites", "kitten")
        self.assertTrue(os.path.isdir(k_dir))

    def test_03_furniture_directory_exists(self):
        f_dir = os.path.join(PROJECT_ROOT, "sprites", "furniture")
        self.assertTrue(os.path.isdir(f_dir))

    def test_04_puppy_sprite_count(self):
        p_dir = os.path.join(PROJECT_ROOT, "sprites", "puppy")
        pngs = [f for f in os.listdir(p_dir) if f.endswith(".png")]
        self.assertEqual(len(pngs), 24)

    def test_05_kitten_sprite_count(self):
        k_dir = os.path.join(PROJECT_ROOT, "sprites", "kitten")
        pngs = [f for f in os.listdir(k_dir) if f.endswith(".png")]
        self.assertEqual(len(pngs), 24)

    def test_06_furniture_sprite_count(self):
        f_dir = os.path.join(PROJECT_ROOT, "sprites", "furniture")
        expected = {"puppy_bed.png", "kitten_bed.png", "puppy_bowl.png", "kitten_bowl.png", "toy_ball.png"}
        actual = set(os.listdir(f_dir))
        self.assertTrue(expected.issubset(actual))

    def test_07_puppy_sprites_valid_rgba(self):
        p_dir = os.path.join(PROJECT_ROOT, "sprites", "puppy")
        for f in os.listdir(p_dir):
            if f.endswith(".png"):
                with Image.open(os.path.join(p_dir, f)) as img:
                    self.assertEqual(img.mode, "RGBA")
                    self.assertEqual(img.size, (128, 128))
                    extrema = img.getextrema()
                    # Alpha channel should have visible pixels
                    self.assertGreater(extrema[3][1], 0)

    def test_08_kitten_sprites_valid_rgba(self):
        k_dir = os.path.join(PROJECT_ROOT, "sprites", "kitten")
        for f in os.listdir(k_dir):
            if f.endswith(".png"):
                with Image.open(os.path.join(k_dir, f)) as img:
                    self.assertEqual(img.mode, "RGBA")
                    self.assertEqual(img.size, (128, 128))
                    extrema = img.getextrema()
                    self.assertGreater(extrema[3][1], 0)

    def test_09_furniture_sprites_valid_rgba(self):
        f_dir = os.path.join(PROJECT_ROOT, "sprites", "furniture")
        for f in ("puppy_bed.png", "kitten_bed.png", "puppy_bowl.png", "kitten_bowl.png", "toy_ball.png"):
            with Image.open(os.path.join(f_dir, f)) as img:
                self.assertEqual(img.mode, "RGBA")
                self.assertGreater(img.size[0], 0)
                self.assertGreater(img.size[1], 0)

    def test_10_ico_file_exists_and_valid(self):
        ico_path = os.path.join(PROJECT_ROOT, "pet.ico")
        self.assertTrue(os.path.isfile(ico_path))
        self.assertGreater(os.path.getsize(ico_path), 5000)
        with Image.open(ico_path) as ico:
            self.assertEqual(ico.format, "ICO")

    def test_11_desktop_pet_exe_exists(self):
        exe_path = os.path.join(PROJECT_ROOT, "Desktop Pet.exe")
        self.assertTrue(os.path.isfile(exe_path))
        self.assertGreater(os.path.getsize(exe_path), 10000)

    def test_12_launcher_scripts_exist(self):
        for script in ("run_pet.pyw", "Launch Desktop Pet.bat", "Launch Desktop Pet.vbs"):
            path = os.path.join(PROJECT_ROOT, script)
            self.assertTrue(os.path.isfile(path), f"Missing {script}")


class TestScreenBoundsAndPhysics(unittest.TestCase):
    """13-18: Bounds, clamping, and basic furniture physics."""

    def setUp(self):
        self.bounds = ScreenBounds(left=0, top=0, right=1920, bottom=1080)

    def test_13_clamp_x(self):
        self.assertEqual(self.bounds.clamp_x(-50, 100), 0.0)
        self.assertEqual(self.bounds.clamp_x(2500, 100), 1820.0)
        self.assertEqual(self.bounds.clamp_x(500, 100), 500.0)

    def test_14_clamp_y(self):
        self.assertEqual(self.bounds.clamp_y(-20, 100), 0.0)
        self.assertEqual(self.bounds.clamp_y(1500, 100), 980.0)
        self.assertEqual(self.bounds.clamp_y(400, 100), 400.0)

    def test_15_furniture_gravity_step(self):
        item = FurnitureItem("test_bed", x=100, y=200, size=80)
        floor_y = 1080 - 80
        item.step_physics(self.bounds, gravity=2.0)
        self.assertGreater(item.vy, 0)
        self.assertGreater(item.y, 200)

    def test_16_furniture_floor_landing(self):
        item = FurnitureItem("test_bed", x=100, y=990, size=80)
        floor_y = 1080 - 80
        for _ in range(50):
            item.step_physics(self.bounds, gravity=1.5, damping=0.25)
        self.assertEqual(item.y, float(floor_y))
        self.assertEqual(item.vy, 0.0)

    def test_17_furniture_dragging_freezes_physics(self):
        item = FurnitureItem("test_bed", x=100, y=200, size=80)
        item.is_dragging = True
        item.step_physics(self.bounds)
        self.assertEqual(item.y, 200.0)
        self.assertEqual(item.vy, 0.0)

    def test_18_furniture_inactive_skips_physics(self):
        item = FurnitureItem("test_bed", x=100, y=200, size=80)
        item.is_active = False
        item.step_physics(self.bounds)
        self.assertEqual(item.y, 200.0)


class TestPetEntityStateMachine(unittest.TestCase):
    """19-25: Pet states, triggers, transitions, and exceptions."""

    def setUp(self):
        self.bounds = ScreenBounds(left=0, top=0, right=1920, bottom=1080)
        self.pet = PetEntity("puppy", "dog", x=200, bounds=self.bounds, pet_size=112)

    def test_19_initial_state_and_pos(self):
        self.assertEqual(self.pet.name, "puppy")
        self.assertEqual(self.pet.species, "dog")
        self.assertEqual(self.pet.state, "WALK")
        self.assertEqual(self.pet.y, float(1080 - 112))

    def test_20_valid_state_transitions(self):
        for st in VALID_STATES:
            self.pet.set_state(st)
            self.assertEqual(self.pet.state, st)
            self.assertEqual(self.pet.frame_index, 0)

    def test_21_invalid_state_raises(self):
        with self.assertRaises(ValueError):
            self.pet.set_state("FLYING")

    def test_22_trigger_snuggle(self):
        self.pet.trigger_snuggle()
        self.assertEqual(self.pet.state, "SNUGGLE")
        self.assertGreater(self.pet.snuggle_timer, 0)
        self.assertLess(self.pet.vy, 0)  # Joyful hop up

    def test_23_eating_state_clearing(self):
        self.pet.is_eating_at_bowl = True
        self.pet.set_state("WALK")
        self.assertFalse(self.pet.is_eating_at_bowl)

    def test_24_sleeping_state_clearing(self):
        self.pet.is_sleeping_in_bed = True
        self.pet.set_state("PLAY")
        self.assertFalse(self.pet.is_sleeping_in_bed)

    def test_25_frame_index_reset_on_state_change(self):
        self.pet.frame_index = 3
        self.pet.set_state("IDLE")
        self.assertEqual(self.pet.frame_index, 0)


class TestMultiPetEngineInteractions(unittest.TestCase):
    """26-38: MultiPetEngine navigation, feeding, sleeping, ball, and cursor."""

    def setUp(self):
        self.bounds = ScreenBounds(left=0, top=0, right=1920, bottom=1080)
        self.engine = MultiPetEngine(self.bounds, pet_size=112)

    def test_26_initial_entities_present(self):
        self.assertIsNotNone(self.engine.puppy)
        self.assertIsNotNone(self.engine.kitten)
        self.assertIn("puppy_bed", self.engine.furniture)
        self.assertIn("kitten_bed", self.engine.furniture)
        self.assertIn("puppy_bowl", self.engine.furniture)
        self.assertIn("kitten_bowl", self.engine.furniture)
        self.assertIn("toy_ball", self.engine.furniture)

    def test_27_puppy_navigates_to_puppy_bed(self):
        self.engine.send_to_bed("puppy")
        self.assertEqual(self.engine.puppy.target_furniture, "puppy_bed")
        # Step simulation until puppy reaches bed
        for _ in range(400):
            self.engine.step_physics()
            if self.engine.puppy.is_sleeping_in_bed:
                break
        self.assertTrue(self.engine.puppy.is_sleeping_in_bed)
        self.assertEqual(self.engine.puppy.state, "SLEEP")

    def test_28_kitten_navigates_to_kitten_bed(self):
        self.engine.send_to_bed("kitten")
        self.assertEqual(self.engine.kitten.target_furniture, "kitten_bed")
        for _ in range(400):
            self.engine.step_physics()
            if self.engine.kitten.is_sleeping_in_bed:
                break
        self.assertTrue(self.engine.kitten.is_sleeping_in_bed)
        self.assertEqual(self.engine.kitten.state, "SLEEP")

    def test_29_puppy_navigates_to_puppy_bowl(self):
        self.engine.send_to_bowl("puppy")
        self.assertEqual(self.engine.puppy.target_furniture, "puppy_bowl")
        for _ in range(400):
            self.engine.step_physics()
            if self.engine.puppy.is_eating_at_bowl:
                break
        self.assertTrue(self.engine.puppy.is_eating_at_bowl)
        self.assertEqual(self.engine.puppy.state, "EAT")

    def test_30_kitten_navigates_to_kitten_bowl(self):
        self.engine.send_to_bowl("kitten")
        self.assertEqual(self.engine.kitten.target_furniture, "kitten_bowl")
        for _ in range(400):
            self.engine.step_physics()
            if self.engine.kitten.is_eating_at_bowl:
                break
        self.assertTrue(self.engine.kitten.is_eating_at_bowl)
        self.assertEqual(self.engine.kitten.state, "EAT")

    def test_31_dragging_bed_wakes_sleeping_puppy(self):
        self.test_27_puppy_navigates_to_puppy_bed()
        bed = self.engine.furniture["puppy_bed"]
        # Move bed far away
        bed.x += 200
        bed.is_dragging = True
        self.engine.step_physics()
        self.assertFalse(self.engine.puppy.is_sleeping_in_bed)
        self.assertEqual(self.engine.puppy.state, "PLAY")

    def test_32_dragging_bowl_interrupts_eating_kitten(self):
        self.test_30_kitten_navigates_to_kitten_bowl()
        bowl = self.engine.furniture["kitten_bowl"]
        bowl.x -= 200
        bowl.is_dragging = True
        self.engine.step_physics()
        self.assertFalse(self.engine.kitten.is_eating_at_bowl)
        self.assertEqual(self.engine.kitten.state, "PLAY")

    def test_33_toggle_toy_ball(self):
        self.assertFalse(self.engine.furniture["toy_ball"].is_active)
        state = self.engine.toggle_toy_ball()
        self.assertTrue(state)
        self.assertTrue(self.engine.furniture["toy_ball"].is_active)
        state = self.engine.toggle_toy_ball()
        self.assertFalse(state)

    def test_34_bounce_toy_ball_activates_ball(self):
        self.engine.bounce_toy_ball()
        ball = self.engine.furniture["toy_ball"]
        self.assertTrue(ball.is_active)
        self.assertLess(ball.vy, 0)

    def test_35_follow_cursor_mode(self):
        self.assertFalse(self.engine.follow_cursor)
        self.engine.toggle_follow_cursor(True)
        self.assertTrue(self.engine.follow_cursor)
        self.engine.cursor_x = 500.0
        self.engine.cursor_y = 500.0

        for _ in range(240):
            self.engine.step_physics()

        # Both puppy and kitten should approach within deadband of cursor offset
        target_puppy = 500.0 - 55.0 - self.engine.puppy.pet_size * 0.5
        target_kitten = 500.0 + 55.0 - self.engine.kitten.pet_size * 0.5
        self.assertAlmostEqual(self.engine.puppy.x, target_puppy, delta=20.0)
        self.assertAlmostEqual(self.engine.kitten.x, target_kitten, delta=20.0)

    def test_35b_mutual_both_eat_and_bed(self):
        # 1. Test call both to eat
        self.engine.toggle_follow_cursor(True)
        self.engine.call_both_to_eat()
        self.assertFalse(self.engine.follow_cursor)
        self.assertEqual(self.engine.puppy.target_furniture, "puppy_bowl")
        self.assertEqual(self.engine.kitten.target_furniture, "kitten_bowl")
        self.assertGreater(self.engine.puppy.lock_eating_timer, 0)
        self.assertGreater(self.engine.kitten.lock_eating_timer, 0)

        # 2. Test bedtime for both
        self.engine.bedtime_for_both()
        self.assertFalse(self.engine.follow_cursor)
        self.assertEqual(self.engine.puppy.target_furniture, "puppy_bed")
        self.assertEqual(self.engine.kitten.target_furniture, "kitten_bed")

        # 3. Test wake up both
        self.engine.wake_up_both()
        self.assertEqual(self.engine.puppy.state, "PLAY")
        self.assertEqual(self.engine.kitten.state, "PLAY")

        # 4. Test both snuggle
        self.engine.both_snuggle()
        self.assertEqual(self.engine.puppy.state, "SNUGGLE")
        self.assertEqual(self.engine.kitten.state, "SNUGGLE")

        # 5. Test put away ball
        self.engine.bounce_toy_ball()
        self.assertTrue(self.engine.furniture["toy_ball"].is_active)
        self.engine.put_away_toy_ball()
        self.assertFalse(self.engine.furniture["toy_ball"].is_active)

    def test_35c_kitten_spawn_location_on_right(self):
        # Kitten must start on the right side near its bed & bowl, facing inward (-1)
        expected_kitten_x = float(self.bounds.right - 260)
        self.assertEqual(self.engine.kitten.x, expected_kitten_x)
        self.assertEqual(self.engine.kitten.direction, -1)
        # Puppy must start on left side near its bed & bowl, facing right (+1)
        expected_puppy_x = float(self.bounds.left + 160)
        self.assertEqual(self.engine.puppy.x, expected_puppy_x)
        self.assertEqual(self.engine.puppy.direction, 1)

    def test_35d_ball_play_smooth_kick(self):
        # Spawn ball and test kicking without velocity clobbering
        self.engine.bounce_toy_ball()
        ball = self.engine.furniture["toy_ball"]
        self.assertTrue(ball.is_active)
        # Position ball directly in puppy kicking range
        ball.x = self.engine.puppy.x + self.engine.puppy.pet_size * 0.5 + 40.0 - ball.size * 0.5
        ball.y = float(self.bounds.bottom - ball.size)
        ball.vx = 0.0
        ball.vy = 0.0
        self.engine.ball_kick_cooldown = 0.0

        # Step physics: puppy should kick ball and hop
        self.engine.step_physics()
        self.assertGreater(self.engine.ball_kick_cooldown, 0.0)
        self.assertLess(ball.vy, 0.0)  # Ball launched up
        self.assertLess(self.engine.puppy.vy, 0.0)  # Puppy pounced up without vy clobbered

    def test_35e_no_random_sleep_on_floor_and_busy_timer(self):
        # Test busy timer blocks random changes
        self.engine.puppy.busy_timer = 20.0
        self.engine.puppy.set_state("WALK")
        for _ in range(30):
            self.engine.pick_random_states()
            self.assertEqual(self.engine.puppy.state, "WALK")

        # Test free pets never randomly sleep on the floor
        self.engine.puppy.busy_timer = 0.0
        self.engine.kitten.busy_timer = 0.0
        for _ in range(100):
            self.engine.pick_random_states()
            self.assertNotEqual(self.engine.puppy.state, "SLEEP")
            self.assertNotEqual(self.engine.kitten.state, "SLEEP")

    def test_36_screen_boundary_bouncing(self):
        pet = self.engine.puppy
        pet.state = "WALK"
        pet.direction = 1
        pet.x = float(self.bounds.right - pet.pet_size - 1)
        self.engine.step_physics()
        self.assertEqual(pet.direction, -1)

    def test_37_advance_frames(self):
        self.engine.puppy.frame_index = 0
        self.engine.kitten.frame_index = 0
        self.engine.advance_frames()
        self.assertEqual(self.engine.puppy.frame_index, 1)
        self.assertEqual(self.engine.kitten.frame_index, 1)

    def test_38_pick_random_states_runs_cleanly(self):
        for _ in range(25):
            self.engine.pick_random_states()
            self.assertIn(self.engine.puppy.state, VALID_STATES)
            self.assertIn(self.engine.kitten.state, VALID_STATES)


class TestGUIAndQtIntegrity(unittest.TestCase):
    """39-44: PyQt6 application, widget lifecycle, particle step, and menus."""

    @classmethod
    def setUpClass(cls):
        # Create headless QGuiApplication for offscreen testing
        from PyQt6.QtWidgets import QApplication
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(["--platform", "offscreen"])

    def test_39_app_controller_init(self):
        from main import DesktopPetApp
        ctrl = DesktopPetApp()
        self.assertIsNotNone(ctrl.puppy_widget)
        self.assertIsNotNone(ctrl.kitten_widget)
        self.assertEqual(len(ctrl.furniture_widgets), 5)
        self.assertIsNotNone(ctrl.tray_icon)

    def test_40_sprite_cache_populated(self):
        from main import DesktopPetApp
        ctrl = DesktopPetApp()
        for pet_name in ("puppy", "kitten"):
            self.assertIn(pet_name, ctrl.sprite_cache)
            for state in VALID_STATES:
                self.assertIn(state, ctrl.sprite_cache[pet_name])
                for idx in range(4):
                    self.assertIn(idx, ctrl.sprite_cache[pet_name][state])
                    self.assertIn(True, ctrl.sprite_cache[pet_name][state][idx])
                    self.assertIn(False, ctrl.sprite_cache[pet_name][state][idx])

    def test_41_pet_snuggle_trigger_and_particles(self):
        from main import DesktopPetApp, FloatingHeart
        ctrl = DesktopPetApp()
        ctrl.trigger_pet_snuggle("puppy")
        self.assertEqual(ctrl.engine.puppy.state, "SNUGGLE")
        self.assertGreater(ctrl.engine.puppy.snuggle_timer, 0)

        # Test heart step
        heart = FloatingHeart(500, 500, char="💖")
        initial_y = heart.pos_y
        heart._step()
        self.assertLess(heart.pos_y, initial_y)
        self.assertLess(heart.opacity, 1.0)
        heart.timer.stop()
        heart.hide()
        heart.deleteLater()

    def test_42_context_menu_action_lambdas(self):
        from main import DesktopPetApp
        ctrl = DesktopPetApp()
        menu = ctrl._build_menu("puppy")
        self.assertIsNotNone(menu)
        # Verify all actions have triggered signals safely callable with bool
        for action in menu.actions():
            if action.menu():
                for sub_action in action.menu().actions():
                    # Invoking trigger with True/False must not raise TypeError
                    sub_action.trigger()
            else:
                action.trigger()

    def test_43_furniture_visibility_toggle(self):
        from main import DesktopPetApp
        ctrl = DesktopPetApp()
        initial_state = ctrl.engine.furniture["puppy_bed"].is_active
        ctrl.toggle_furniture_visibility()
        self.assertNotEqual(ctrl.engine.furniture["puppy_bed"].is_active, initial_state)
        ctrl.toggle_furniture_visibility()
        self.assertEqual(ctrl.engine.furniture["puppy_bed"].is_active, initial_state)

    def test_44_pet_scaling(self):
        from main import DesktopPetApp
        ctrl = DesktopPetApp()
        ctrl.set_pet_size(144)
        self.assertEqual(ctrl.pet_size, 144)
        self.assertEqual(ctrl.puppy_widget.width(), 144)
        self.assertEqual(ctrl.kitten_widget.width(), 144)

    def test_45_settings_button_widget(self):
        from main import DesktopPetApp, SettingsButtonWidget
        ctrl = DesktopPetApp()
        self.assertIsNotNone(ctrl.settings_btn)
        self.assertIsInstance(ctrl.settings_btn, SettingsButtonWidget)
        self.assertEqual(ctrl.settings_btn.width(), 44)
        self.assertEqual(ctrl.settings_btn.height(), 44)
        self.assertTrue(ctrl.settings_btn.isVisible())

        # Test hover event simulation
        ctrl.settings_btn.is_hovered = True
        self.assertTrue(ctrl.settings_btn.is_hovered)
        ctrl.settings_btn.is_hovered = False
        self.assertFalse(ctrl.settings_btn.is_hovered)

    def test_46_settings_button_click_and_drag(self):
        from PyQt6.QtCore import QPointF
        from PyQt6.QtGui import QMouseEvent
        from PyQt6.QtCore import Qt, QPoint
        from main import DesktopPetApp

        ctrl = DesktopPetApp()
        btn = ctrl.settings_btn

        # Test drag behavior
        press_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(20, 20),
            QPointF(500, 500),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        btn.mousePressEvent(press_event)
        self.assertEqual(btn.press_pos, QPoint(500, 500))

        # Small move (< 4px) should not mark dragging
        move_small = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(21, 21),
            QPointF(502, 502),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        btn.mouseMoveEvent(move_small)
        self.assertFalse(btn.is_dragging)

        # Larger move (> 4px) should mark dragging
        move_large = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(35, 35),
            QPointF(515, 515),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        btn.mouseMoveEvent(move_large)
        self.assertTrue(btn.is_dragging)

        # Release ends drag
        release_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(35, 35),
            QPointF(515, 515),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        btn.mouseReleaseEvent(release_event)
        self.assertFalse(btn.is_dragging)


if __name__ == "__main__":
    unittest.main()
