import os
import random
import sys
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pet_engine import PetEngine, ScreenBounds, VALID_STATES
from sprite_generator import ensure_sprites_exist

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SPRITE_ROOT = os.path.join(BASE_DIR, "sprites")
SPRITE_DIR = os.path.join(SPRITE_ROOT, "cute")          # default (cute) style
REAL_DIR = os.path.join(SPRITE_ROOT, "real")


class TestDesktopPetV3Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_sprites_exist(SPRITE_DIR)
        ensure_sprites_exist(REAL_DIR)

    def setUp(self):
        self.bounds = ScreenBounds(left=0, top=0, right=1920, bottom=1040)
        self.engine = PetEngine(bounds=self.bounds, pet_size=112, walk_speed=2.5, gravity=1.2)

    def test_01_all_25_sprite_assets_exist_and_valid(self):
        expected_files = ["toy.png"]
        for state in VALID_STATES:
            for i in range(1, 5):
                expected_files.append(f"{state.lower()}_{i}.png")

        self.assertEqual(len(expected_files), 25)
        for fname in expected_files:
            fpath = os.path.join(SPRITE_DIR, fname)
            self.assertTrue(os.path.isfile(fpath), f"Missing sprite file: {fname}")
            with Image.open(fpath) as img:
                self.assertEqual(img.mode, "RGBA")
                self.assertEqual(img.size, (128, 128))
                self.assertIsNotNone(img.getbbox())

    def test_02_state_transitions_and_validation(self):
        for state in VALID_STATES:
            self.engine.frame_index = 3
            self.engine.set_state(state)
            self.assertEqual(self.engine.state, state)
            self.assertEqual(self.engine.frame_index, 0)

        with self.assertRaises(ValueError):
            self.engine.set_state("UNKNOWN_STATE")

    def test_03_frame_cycling_wraps_cleanly(self):
        self.engine.set_state("EAT")
        visited = [self.engine.advance_frame() for _ in range(8)]
        self.assertEqual(visited, [1, 2, 3, 0, 1, 2, 3, 0])

    def test_04_horizontal_walking_and_screen_edge_bouncing(self):
        self.engine.set_state("WALK")
        self.engine.x = float(self.bounds.right - self.engine.pet_size - 1)
        self.engine.direction = 1
        self.engine.step_physics()
        self.assertEqual(self.engine.x, float(self.bounds.right - self.engine.pet_size))
        self.assertEqual(self.engine.direction, -1)

    def test_05_gravity_fall_and_bounce_settling(self):
        self.engine.y = 200.0
        self.engine.vy = 0.0
        for _ in range(300):
            self.engine.step_physics()
        self.assertEqual(self.engine.y, self.engine.floor_y)
        self.assertEqual(self.engine.vy, 0.0)

    def test_06_drag_clamping_and_throw_velocity_limits(self):
        self.engine.start_drag()
        self.engine.drag_to(-5000.0, -3000.0)
        self.assertEqual(self.engine.x, float(self.bounds.left))
        self.assertEqual(self.engine.y, float(self.bounds.top))

        self.engine.drag_to(99999.0, 99999.0)
        self.engine.end_drag()
        self.assertFalse(self.engine.is_dragging)
        self.assertLessEqual(abs(self.engine.vx), 14.0)
        self.assertLessEqual(abs(self.engine.vy), 12.0)

    def test_07_dynamic_resolution_or_pet_resize(self):
        smaller_bounds = ScreenBounds(left=0, top=0, right=1280, bottom=720)
        self.engine.x = 1800.0
        self.engine.y = 900.0
        self.engine.update_bounds(smaller_bounds)
        self.assertLessEqual(self.engine.x, 1280 - self.engine.pet_size)
        self.assertEqual(self.engine.y, 720 - self.engine.pet_size)

    def test_08_jump_impulse_and_landing_recovery(self):
        self.engine.trigger_jump()
        self.assertEqual(self.engine.state, "JUMP")
        self.assertLess(self.engine.vy, 0.0)
        # Step once to lift off floor
        self.engine.step_physics()
        self.assertLess(self.engine.y, self.engine.floor_y)
        # Step until landed and settled back to IDLE
        for _ in range(250):
            self.engine.step_physics()
        self.assertEqual(self.engine.y, self.engine.floor_y)
        self.assertEqual(self.engine.state, "IDLE")

    def test_09_feed_cookie_snack_state(self):
        self.engine.vx = 5.0
        self.engine.feed_snack()
        self.assertEqual(self.engine.state, "EAT")
        self.assertEqual(self.engine.vx, 0.0)

    def test_10_interactive_toy_spawn_and_autonomous_chase(self):
        random.seed(2)
        self.engine.x = 200.0
        self.engine.spawn_toy(target_x=700.0, target_y=self.engine.toy_floor_y)
        self.assertTrue(self.engine.toy_active)
        # Let pet chase the toy ball to the right
        for _ in range(200):
            self.engine.step_physics()
        # Pet should have walked close to toy_x and switched to PLAY
        dist = abs((self.engine.x + self.engine.pet_size * 0.5) - (self.engine.toy_x + self.engine.toy_size * 0.5))
        self.assertLessEqual(dist, 50.0)
        self.assertEqual(self.engine.state, "PLAY")

    def test_11_bounce_toy_ball_method(self):
        self.assertFalse(self.engine.toy_active)
        self.engine.bounce_toy(impulse_x=4.0, impulse_y=-8.5)
        self.assertTrue(self.engine.toy_active)
        self.assertEqual(self.engine.toy_vy, -8.5)
        self.assertEqual(self.engine.toy_vx, 4.0)

    def test_12_no_duplicate_toy_ball_in_play_sprites(self):
        # Inspect play_1..4 sprites: ensure no blue toy ball pixels exist
        # TOY_BASE was (64, 178, 255), TOY_OUTLINE was (24, 78, 128)
        for i in range(1, 5):
            fpath = os.path.join(SPRITE_DIR, f"play_{i}.png")
            with Image.open(fpath) as img:
                rgba = img.convert("RGBA")
                w, h = rgba.size
                for y in range(h):
                    for x in range(w):
                        r, g, b, a = rgba.getpixel((x, y))
                        if a > 0:
                            # Verify no blue toy ball pixels (where blue dominates over red)
                            is_blue_toy_pixel = (b > 180 and b > r + 60 and g > 100)
                            self.assertFalse(
                                is_blue_toy_pixel,
                                f"Found duplicate baked-in toy ball pixel in {fpath} at ({x}, {y})!"
                            )

    def test_13_rapid_toggle_toy_spawn_and_despawn(self):
        # Stress-test 100 rapid spawn/despawn cycles under various pet states
        states = ["WALK", "PLAY", "EAT", "SLEEP", "JUMP", "IDLE"]
        for i in range(100):
            st = states[i % len(states)]
            self.engine.set_state(st)
            self.engine.spawn_toy()
            self.assertTrue(self.engine.toy_active)
            self.engine.step_physics()
            self.engine.despawn_toy()
            self.assertFalse(self.engine.toy_active)
            self.engine.step_physics()
            # Invariant: pet coords must remain sane
            self.assertGreaterEqual(self.engine.x, self.bounds.left)
            self.assertLessEqual(self.engine.x, self.bounds.right - self.engine.pet_size)

    def test_14_throw_toy_ball_extreme_velocities_and_ceiling_clamp(self):
        self.engine.spawn_toy(target_x=500.0, target_y=500.0)
        # Extreme upward and sideways velocity
        self.engine.toy_vx = 350.0
        self.engine.toy_vy = -800.0
        for _ in range(300):
            self.engine.step_physics()
        # Toy must remain inside bounds
        self.assertGreaterEqual(self.engine.toy_x, self.bounds.left)
        self.assertLessEqual(self.engine.toy_x, self.bounds.right - self.engine.toy_size)
        self.assertGreaterEqual(self.engine.toy_y, self.bounds.top)
        self.assertLessEqual(self.engine.toy_y, self.engine.toy_floor_y)
        # Once settled, vertical velocity should be 0
        self.assertEqual(self.engine.toy_y, self.engine.toy_floor_y)
        self.assertEqual(self.engine.toy_vy, 0.0)

    def test_15_simultaneous_drag_and_release(self):
        self.engine.spawn_toy(target_x=300.0, target_y=300.0)
        self.engine.start_drag()
        self.engine.drag_to(100.0, 100.0)
        self.engine.toy_dragging = True
        self.engine.toy_x = 900.0
        self.engine.toy_y = 150.0

        # Step physics during drag
        self.engine.step_physics()
        self.assertEqual(self.engine.x, 100.0)
        self.assertEqual(self.engine.y, 100.0)

        # Release both
        self.engine.end_drag()
        self.engine.toy_dragging = False
        self.assertFalse(self.engine.is_dragging)
        self.assertFalse(self.engine.toy_dragging)

        # Step until both settle
        for _ in range(400):
            self.engine.step_physics()

        self.assertEqual(self.engine.y, self.engine.floor_y)
        self.assertEqual(self.engine.toy_y, self.engine.toy_floor_y)

    def test_16_aggressive_fuzzing_under_load(self):
        # 1,000 steps of random inputs, impulses, jumps, state changes, bounds updates
        rng = random.Random(42)
        for step in range(1000):
            action = rng.choice(["jump", "eat", "spawn_toy", "despawn_toy", "bounce_toy", "drag", "step", "change_bounds"])
            if action == "jump":
                self.engine.trigger_jump()
            elif action == "eat":
                self.engine.feed_snack()
            elif action == "spawn_toy":
                self.engine.spawn_toy()
            elif action == "despawn_toy":
                self.engine.despawn_toy()
            elif action == "bounce_toy":
                self.engine.bounce_toy(impulse_x=rng.uniform(-10, 10), impulse_y=rng.uniform(-12, -2))
            elif action == "drag":
                self.engine.start_drag()
                self.engine.drag_to(rng.uniform(-200, 2500), rng.uniform(-200, 1500))
                self.engine.end_drag()
            elif action == "change_bounds":
                new_w = rng.randint(800, 2560)
                new_h = rng.randint(600, 1440)
                self.engine.update_bounds(ScreenBounds(0, 0, new_w, new_h))
            self.engine.step_physics()

            # Assert invariants at every step
            self.assertIn(self.engine.state, VALID_STATES)
            self.assertGreaterEqual(self.engine.x, self.engine.bounds.left - 0.001)
            self.assertLessEqual(self.engine.x, self.engine.bounds.right - self.engine.pet_size + 0.001)
            self.assertGreaterEqual(self.engine.y, self.engine.bounds.top - 0.001)
            self.assertLessEqual(self.engine.y, self.engine.floor_y + 0.001)
            if self.engine.toy_active and not self.engine.toy_dragging:
                self.assertGreaterEqual(self.engine.toy_x, self.engine.bounds.left - 0.001)
                self.assertLessEqual(self.engine.toy_x, self.engine.bounds.right - self.engine.toy_size + 0.001)
                self.assertGreaterEqual(self.engine.toy_y, self.engine.bounds.top - 0.001)
                self.assertLessEqual(self.engine.toy_y, self.engine.toy_floor_y + 0.001)

    def test_17_gui_widget_initialization_and_resizing(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        self.assertEqual(pet.pet_size, 112)
        self.assertIsNotNone(pet.engine)

        for sz in (80, 112, 144):
            pet.change_size(sz)
            self.assertEqual(pet.pet_size, sz)
            self.assertEqual(pet.engine.pet_size, sz)

    def test_18_gui_toy_widget_toggle_and_bounce(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        self.assertFalse(pet.engine.toy_active)

        # Spawn ball
        pet.toggle_toy_ball()
        self.assertTrue(pet.engine.toy_active)

        # Bounce ball
        pet.bounce_toy_ball()
        self.assertLess(pet.engine.toy_vy, 0.0)

        # Put away ball
        pet.toggle_toy_ball()
        self.assertFalse(pet.engine.toy_active)

    def test_19_gui_context_menu_actions_and_force_states(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)

        # Build context menu with ball away
        menu1 = pet._build_context_menu()
        self.assertGreater(len(menu1.actions()), 5)

        # Build context menu with ball active
        pet.toggle_toy_ball()
        menu2 = pet._build_context_menu()
        self.assertGreater(len(menu2.actions()), 5)

        # Force all states
        for st in ("IDLE", "WALK", "PLAY", "SLEEP", "EAT", "JUMP"):
            pet.force_state(st)
            if st == "EAT":
                self.assertEqual(pet.engine.state, "EAT")
            elif st == "JUMP":
                self.assertEqual(pet.engine.state, "JUMP")
            else:
                self.assertEqual(pet.engine.state, st)

    def test_20_gui_continuous_physics_and_animation_loop(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)

        # Run 100 physics and animation iterations simulating live app
        for _ in range(100):
            pet.on_physics_tick()
            pet.on_animation_tick()
        self.assertIn(pet.engine.state, VALID_STATES)

    @staticmethod
    def _count_color(img, rgb, tol=0):
        rgba = img.convert("RGBA")
        n = 0
        for y in range(rgba.height):
            for x in range(rgba.width):
                p = rgba.getpixel((x, y))
                if p[3] > 0 and all(abs(p[k] - rgb[k]) <= tol for k in range(3)):
                    n += 1
        return n

    def test_21_chibi_griffin_has_paws_with_pink_toe_beans_and_golden_feet(self):
        # Standing/hovering frames must show the cute back-paw toe beans and golden front feet
        for frame in (1, 2, 3, 4):
            fpath = os.path.join(SPRITE_DIR, f"idle_{frame}.png")
            with Image.open(fpath) as img:
                self.assertGreaterEqual(self._count_color(img, (255, 158, 175)), 4, f"No pink toe beans in {fpath}")
                self.assertGreaterEqual(self._count_color(img, (255, 205, 80)), 20, f"No golden front feet in {fpath}")

    def test_22_chibi_face_has_eyes_beak_and_blush(self):
        # Every awake idle frame must show eyes (open, or blink line) and the tiny golden beak
        for frame in (1, 2, 3, 4):
            fpath = os.path.join(SPRITE_DIR, f"idle_{frame}.png")
            with Image.open(fpath) as img:
                self.assertGreaterEqual(self._count_color(img, (50, 30, 40)), 8, f"Missing eyes in {fpath}")
                self.assertGreaterEqual(self._count_color(img, (255, 200, 70)), 10, f"Missing beak in {fpath}")


    def test_23_real_griffin_sprites_exist_and_are_valid(self):
        names = ["toy.png"] + [f"{s.lower()}_{i}.png" for s in VALID_STATES for i in range(1, 5)]
        for fname in names:
            with Image.open(os.path.join(REAL_DIR, fname)) as img:
                self.assertEqual(img.mode, "RGBA")
                self.assertEqual(img.size, (128, 128))
                self.assertIsNotNone(img.getbbox())

    def test_24_real_griffin_has_hooked_golden_beak_and_amber_eye(self):
        for frame in (1, 2, 3):
            with Image.open(os.path.join(REAL_DIR, f"idle_{frame}.png")) as img:
                self.assertGreaterEqual(self._count_color(img, (248, 192, 50)), 20, "Missing golden beak")
                self.assertGreaterEqual(self._count_color(img, (255, 176, 34)), 4, "Missing amber eye")

    def test_25_real_and_cute_sprites_are_different_art(self):
        with Image.open(os.path.join(SPRITE_DIR, "idle_1.png")) as a, Image.open(os.path.join(REAL_DIR, "idle_1.png")) as b:
            self.assertNotEqual(a.tobytes(), b.tobytes())

    def test_26_gui_switch_between_cute_and_real_griffin(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        self.assertEqual(pet.style, "cute")
        pet.change_style("real")
        self.assertEqual(pet.style, "real")
        self.assertTrue(pet.sprite_dir.endswith("real"))
        for _ in range(6):
            pet.on_animation_tick()
        pet.change_style("cute")
        self.assertEqual(pet.style, "cute")
        pet.change_style("nonsense")
        self.assertEqual(pet.style, "cute")
        real_pet = CozyDesktopPet(pet_size=112, style="real")
        self.assertEqual(real_pet.style, "real")

    def test_27_continuous_flying_mode_toggle_and_flight_physics(self):
        self.assertFalse(self.engine.flying_mode)
        self.engine.toggle_flying(True)
        self.assertTrue(self.engine.flying_mode)
        # Advance physics multiple steps: pet should lift and soar in the air above floor
        for _ in range(50):
            self.engine.step_physics()
        self.assertLess(self.engine.y, self.engine.floor_y)
        self.assertIn(self.engine.state, ("WALK", "JUMP"))
        # Pet stays in the air across many iterations
        for _ in range(100):
            self.engine.step_physics()
        self.assertLess(self.engine.y, self.engine.floor_y)
        # Toggle flying off: should settle back down
        self.engine.toggle_flying(False)
        self.assertFalse(self.engine.flying_mode)

    def test_28_gui_toggle_flying_mode(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        self.assertFalse(pet.engine.flying_mode)
        pet.toggle_flying_mode()
        self.assertTrue(pet.engine.flying_mode)
        # Step physics and animation
        for _ in range(20):
            pet.on_physics_tick()
            pet.on_animation_tick()
        self.assertLess(pet.engine.y, pet.engine.floor_y)
        # Forcing a sleep/idle state disables flying mode
        pet.force_state("SLEEP")
        self.assertFalse(pet.engine.flying_mode)

    def test_29_permanent_bed_and_food_bowl_state_toggles(self):
        # Bed toggle and position clamps
        self.assertFalse(self.engine.bed_active)
        self.engine.toggle_bed(True)
        self.assertTrue(self.engine.bed_active)
        self.engine.update_bounds(ScreenBounds(0, 0, 800, 600))
        self.assertGreaterEqual(self.engine.bed_x, 0)
        self.assertLessEqual(self.engine.bed_x, 800 - self.engine.bed_size)
        self.engine.toggle_bed(False)
        self.assertFalse(self.engine.bed_active)

        # Food bowl toggle and position clamps
        self.assertFalse(self.engine.bowl_active)
        self.engine.toggle_bowl(True)
        self.assertTrue(self.engine.bowl_active)
        self.engine.update_bounds(ScreenBounds(0, 0, 800, 600))
        self.assertGreaterEqual(self.engine.bowl_x, 0)
        self.assertLessEqual(self.engine.bowl_x, 800 - self.engine.bowl_size)
        self.engine.toggle_bowl(False)
        self.assertFalse(self.engine.bowl_active)

    def test_30_gui_bed_and_food_bowl_widgets(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        
        # Test bed widget toggle
        self.assertFalse(pet.bed_widget.isVisible())
        pet.toggle_bed(True)
        self.assertTrue(pet.bed_widget.isVisible())
        self.assertTrue(pet.engine.bed_active)
        pet.toggle_bed(False)
        self.assertFalse(pet.bed_widget.isVisible())
        self.assertFalse(pet.engine.bed_active)

        # Test food bowl widget toggle
        self.assertFalse(pet.bowl_widget.isVisible())
        pet.toggle_food_bowl(True)
        self.assertTrue(pet.bowl_widget.isVisible())
        self.assertTrue(pet.engine.bowl_active)
        pet.toggle_food_bowl(False)
        self.assertFalse(pet.bowl_widget.isVisible())
        self.assertFalse(pet.engine.bowl_active)

    def test_31_bed_and_bowl_gravity_falling_physics(self):
        # Bed falls under gravity and settles at floor
        self.engine.toggle_bed(True)
        self.engine.bed_y = 100.0
        self.engine.bed_vy = 0.0
        floor = self.engine.bed_floor_y
        for _ in range(80):
            self.engine.step_physics()
        self.assertEqual(self.engine.bed_y, floor)
        self.assertEqual(self.engine.bed_vy, 0.0)

        # Food bowl falls under gravity and settles at floor
        self.engine.toggle_bowl(True)
        self.engine.bowl_y = 50.0
        self.engine.bowl_vy = 0.0
        b_floor = self.engine.bowl_floor_y
        for _ in range(80):
            self.engine.step_physics()
        self.assertEqual(self.engine.bowl_y, b_floor)
        self.assertEqual(self.engine.bowl_vy, 0.0)

    def test_32_go_to_bed_and_go_to_bowl_navigation(self):
        # Position pet on the left
        self.engine.x = 50.0
        self.engine.y = self.engine.floor_y
        self.engine.set_state("IDLE")

        # Position bed further to the right
        self.engine.toggle_bed(True)
        self.engine.bed_x = 300.0
        self.engine.bed_y = self.engine.bed_floor_y

        # Command to nap in bed
        self.engine.go_to_bed()
        self.assertEqual(self.engine.target_action, "NAP_BED")
        self.assertEqual(self.engine.state, "WALK")

        # Step physics until arrived
        for _ in range(120):
            self.engine.step_physics()
        self.assertIsNone(self.engine.target_action)
        self.assertEqual(self.engine.state, "SLEEP")
        bed_center_x = self.engine.bed_x + (self.engine.bed_size - self.engine.pet_size) * 0.5
        self.assertAlmostEqual(self.engine.x, bed_center_x, delta=1.0)

        # Position bowl to the right
        self.engine.toggle_bowl(True)
        self.engine.bowl_x = 500.0
        self.engine.bowl_y = self.engine.bowl_floor_y

        # Command to eat from bowl
        self.engine.go_to_bowl()
        self.assertEqual(self.engine.target_action, "EAT_BOWL")
        self.assertEqual(self.engine.state, "WALK")

        for _ in range(120):
            self.engine.step_physics()
        self.assertIsNone(self.engine.target_action)
        self.assertEqual(self.engine.state, "EAT")
        self.assertTrue(self.engine.is_eating_at_bowl)

    def test_33_eating_at_bowl_and_moving_bowl_reaction(self):
        self.engine.toggle_bowl(True)
        self.engine.bowl_x = 400.0
        self.engine.bowl_y = self.engine.bowl_floor_y
        self.engine.x = 350.0
        self.engine.y = self.engine.floor_y
        self.engine.set_state("WALK")

        self.engine.go_to_bowl()
        for _ in range(60):
            self.engine.step_physics()
        self.assertEqual(self.engine.state, "EAT")
        self.assertTrue(self.engine.is_eating_at_bowl)

        # Move bowl away while eating!
        self.engine.bowl_x = 700.0
        self.engine.on_bowl_moved()
        self.assertFalse(self.engine.is_eating_at_bowl)
        self.assertEqual(self.engine.target_action, "EAT_BOWL")
        self.assertEqual(self.engine.state, "JUMP")
        self.assertLess(self.engine.vy, 0)  # Startled hop!

        # Pet chases after the displaced bowl!
        for _ in range(120):
            self.engine.step_physics()
        self.assertEqual(self.engine.state, "EAT")
        self.assertTrue(self.engine.is_eating_at_bowl)
        self.assertIsNone(self.engine.target_action)

    def test_34_napping_in_bed_and_moving_bed_reaction(self):
        self.engine.toggle_bed(True)
        self.engine.bed_x = 300.0
        self.engine.bed_y = self.engine.bed_floor_y
        self.engine.x = 250.0
        self.engine.y = self.engine.floor_y
        self.engine.set_state("WALK")

        self.engine.go_to_bed()
        for _ in range(60):
            self.engine.step_physics()
        self.assertEqual(self.engine.state, "SLEEP")
        self.assertTrue(self.engine.is_sleeping_in_bed)
        expected_cushion_y = self.engine.bed_y + self.engine.bed_size - self.engine.pet_size - 8
        self.assertAlmostEqual(self.engine.y, expected_cushion_y, delta=1.0)

        # Drag bed away while sleeping!
        self.engine.bed_x = 600.0
        self.engine.bed_dragging = True
        self.engine.step_physics()
        self.assertFalse(self.engine.is_sleeping_in_bed)
        self.assertEqual(self.engine.target_action, "NAP_BED")
        self.assertEqual(self.engine.state, "JUMP")
        self.assertLess(self.engine.vy, 0)  # Surprised hop awake!

        # Release bed and let pet chase back and settle
        self.engine.bed_dragging = False
        for _ in range(120):
            self.engine.step_physics()
        self.assertEqual(self.engine.state, "SLEEP")
        self.assertTrue(self.engine.is_sleeping_in_bed)
        self.assertIsNone(self.engine.target_action)

    def test_35_follow_cursor_mode_toggle_and_ground_tracking(self):
        self.assertFalse(self.engine.follow_cursor)
        self.engine.toggle_follow_cursor(True)
        self.assertTrue(self.engine.follow_cursor)

        # Pet at 500, cursor at 800 -> Pet should move right
        self.engine.x = 500.0
        self.engine.cursor_x = 800.0
        self.engine.cursor_y = self.engine.floor_y
        self.engine.step_physics()
        self.assertEqual(self.engine.direction, 1)
        self.assertGreater(self.engine.x, 500.0)

        # Pet at 500, cursor at 200 -> Pet should move left
        self.engine.x = 500.0
        self.engine.cursor_x = 200.0
        self.engine.step_physics()
        self.assertEqual(self.engine.direction, -1)
        self.assertLess(self.engine.x, 500.0)

        # Pet right at cursor -> Stops and switches to IDLE
        self.engine.x = 300.0
        self.engine.cursor_x = 300.0 + self.engine.pet_size * 0.5
        self.engine.set_state("WALK")
        self.engine.step_physics()
        self.assertEqual(self.engine.state, "IDLE")

        # Random state changes should not override follow_cursor
        next_s = self.engine.pick_next_state()
        self.assertEqual(next_s, self.engine.state)

    def test_36_follow_cursor_mode_aerial_flight_tracking(self):
        self.engine.toggle_flying(True)
        self.engine.toggle_follow_cursor(True)
        self.engine.x = 200.0
        self.engine.y = 200.0
        self.engine.cursor_x = 600.0
        self.engine.cursor_y = 500.0
        self.engine.step_physics()
        self.assertEqual(self.engine.state, "JUMP")
        self.assertGreater(self.engine.x, 200.0)
        self.assertGreater(self.engine.y, 200.0)

    def test_37_snuggle_affection_and_floating_hearts(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        pet.trigger_snuggle()
        self.assertEqual(pet.engine.state, "PLAY")
        self.assertGreater(pet.engine.snuggle_timer, 0.0)
        self.assertGreater(len(pet.active_hearts), 0)
        # Verify hearts advance and clean up
        for h in pet.active_hearts:
            h._step()
        pet.close()

    def test_38_multi_click_and_double_click_triggers_snuggle_not_eat(self):
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QMouseEvent
        from PyQt6.QtCore import QPointF, Qt
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)

        # Double-click event
        ev_double = QMouseEvent(
            QMouseEvent.Type.MouseButtonDblClick,
            QPointF(20.0, 20.0),
            QPointF(100.0, 100.0),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        pet.mouseDoubleClickEvent(ev_double)
        # Must be PLAY (snuggle), NOT EAT!
        self.assertEqual(pet.engine.state, "PLAY")
        self.assertNotEqual(pet.engine.state, "EAT")
        pet.close()

    def test_39_context_menu_has_follow_cursor_and_no_chill(self):
        from PyQt6.QtWidgets import QApplication
        from main import CozyDesktopPet
        app = QApplication.instance() or QApplication(["test", "-platform", "offscreen"])
        pet = CozyDesktopPet(pet_size=112)
        menu = pet._build_context_menu()
        action_texts = [a.text() for a in menu.actions()]

        # Verify Follow Mouse Cursor and Snuggle are present
        self.assertTrue(any("Follow Mouse Cursor" in t for t in action_texts))
        self.assertTrue(any("Snuggle & Cuddle" in t for t in action_texts))

        # Verify "Rest on Taskbar / Chill" is REMOVED
        self.assertFalse(any("Chill" in t or "Rest on Taskbar" in t for t in action_texts))
        pet.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
