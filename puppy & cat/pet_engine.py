"""
Multi-Pet Physics & AI State Machine Engine for Puppy & Cat Desktop Pets.
Manages:
- Dual Pet Entities: Puppy 🐶 and Kitten 🐱
- 4 Dedicated Interactive Furniture Items:
  * Puppy Bed (blue bolster with bone)
  * Kitten Bed (pink nest with paw)
  * Puppy Bowl (kibbles & water)
  * Kitten Bowl (tuna & milk)
  * Play Toy Ball (shared bouncy ball)
- Independent and social AI, furniture navigation, cursor following, and physics.
"""
import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

VALID_STATES = ("IDLE", "WALK", "PLAY", "SLEEP", "EAT", "SNUGGLE")


@dataclass
class ScreenBounds:
    left: int = 0
    top: int = 0
    right: int = 1920
    bottom: int = 1040

    def clamp_x(self, x: float, size: int) -> float:
        max_x = max(self.left, self.right - size)
        return float(max(self.left, min(x, max_x)))

    def clamp_y(self, y: float, size: int) -> float:
        max_y = max(self.top, self.bottom - size)
        return float(max(self.top, min(y, max_y)))


class FurnitureItem:
    """An interactive physical furniture item on the desktop floor."""

    def __init__(self, item_type: str, x: float, y: float, size: int = 80):
        self.item_type = item_type
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.size = size
        self.is_active = True
        self.is_dragging = False

    def step_physics(self, bounds: ScreenBounds, gravity: float = 1.15, damping: float = 0.28) -> None:
        if self.is_dragging or not self.is_active:
            return

        is_ball = (self.item_type == "toy_ball")
        eff_gravity = 0.85 if is_ball else gravity
        eff_damping = 0.80 if is_ball else damping
        eff_decay = 0.988 if is_ball else 0.94
        min_bounce = 1.3 if is_ball else 2.8

        floor_y = float(bounds.bottom - self.size)
        if self.y < floor_y or abs(self.vy) > 0.05 or abs(self.vx) > 0.05:
            self.vy += eff_gravity
            self.y += self.vy
            self.x += self.vx
            self.vx *= eff_decay

            # Ceiling clamp
            if self.y < bounds.top:
                self.y = float(bounds.top)
                self.vy = abs(self.vy) * (0.7 if is_ball else 0.3)

            # Horizontal boundary clamp
            max_x = float(bounds.right - self.size)
            if self.x <= bounds.left:
                self.x = float(bounds.left)
                self.vx = abs(self.vx) * (0.8 if is_ball else 0.5)
            elif self.x >= max_x:
                self.x = max_x
                self.vx = -abs(self.vx) * (0.8 if is_ball else 0.5)

            # Floor landing
            if self.y >= floor_y:
                self.y = floor_y
                if abs(self.vy) > min_bounce:
                    self.vy = -abs(self.vy) * eff_damping
                else:
                    self.vy = 0.0
                    if not is_ball or abs(self.vx) < 0.15:
                        self.vx = 0.0


class PetEntity:
    """An individual pet entity (Puppy or Kitten) with distinct AI and physics."""

    def __init__(
        self,
        name: str,
        species: str,
        x: float,
        bounds: ScreenBounds,
        pet_size: int = 112,
        walk_speed: float = 2.5,
    ):
        self.name = name
        self.species = species
        self.pet_size = pet_size
        self.walk_speed = walk_speed
        self.state = "WALK"
        self.frame_index = 0
        self.direction = 1
        self.is_dragging = False

        self.floor_y = float(bounds.bottom - self.pet_size)
        self.x = float(x)
        self.y = self.floor_y
        self.vx = 0.0
        self.vy = 0.0

        self.target_furniture: Optional[str] = None
        self.is_sleeping_in_bed = False
        self.is_eating_at_bowl = False
        self.snuggle_timer = 0.0
        self.lock_eating_timer = 0.0
        self.lock_sleep_timer = 0.0
        self.busy_timer = 0.0

    def set_state(self, new_state: str) -> None:
        if new_state not in VALID_STATES:
            raise ValueError(f"Invalid state '{new_state}'")
        if new_state != "EAT":
            self.is_eating_at_bowl = False
            if not (self.target_furniture and "bowl" in self.target_furniture):
                self.lock_eating_timer = 0.0
        if new_state != "SLEEP":
            self.is_sleeping_in_bed = False
            if not (self.target_furniture and "bed" in self.target_furniture):
                self.lock_sleep_timer = 0.0
        self.state = new_state
        self.frame_index = 0

    def trigger_snuggle(self) -> None:
        self.set_state("SNUGGLE")
        self.snuggle_timer = 4.0
        self.busy_timer = 8.0
        self.target_furniture = None
        self.is_eating_at_bowl = False
        self.is_sleeping_in_bed = False
        self.lock_eating_timer = 0.0
        self.lock_sleep_timer = 0.0
        self.vy = -5.0  # Joyful hop


class MultiPetEngine:
    """Orchestrates both Puppy & Kitten and their 4 furniture items."""

    def __init__(self, bounds: ScreenBounds, pet_size: int = 112):
        self.bounds = bounds
        self.pet_size = pet_size
        self.gravity = 1.15
        self.bounce_damping = 0.28
        self.follow_cursor = False
        self.cursor_x = 0.0
        self.cursor_y = 0.0
        self.ball_kick_cooldown = 0.0

        floor = float(self.bounds.bottom)
        # Position puppy on left (near its bed & bowl), kitten on right (near its bed & bowl)
        puppy_start_x = float(self.bounds.left + 160)
        kitten_start_x = float(self.bounds.right - 260)

        self.puppy = PetEntity("puppy", "dog", puppy_start_x, self.bounds, pet_size=pet_size, walk_speed=2.6)
        self.kitten = PetEntity("kitten", "cat", kitten_start_x, self.bounds, pet_size=pet_size, walk_speed=2.3)
        self.kitten.direction = -1  # Starts facing inwards towards the center

        # 4 Permanent Furniture Items spaced neatly on desktop floor:
        # [Puppy Bed]  [Puppy Bowl]  ...  [Kitten Bowl]  [Kitten Bed]
        bed_w, bed_h = 96, 96
        bowl_w, bowl_h = 76, 76

        self.furniture: Dict[str, FurnitureItem] = {
            "puppy_bed": FurnitureItem("puppy_bed", x=float(self.bounds.left + 50), y=floor - bed_h, size=bed_w),
            "puppy_bowl": FurnitureItem("puppy_bowl", x=float(self.bounds.left + 290), y=floor - bowl_h, size=bowl_w),
            "kitten_bowl": FurnitureItem("kitten_bowl", x=float(self.bounds.right - 370), y=floor - bowl_h, size=bowl_w),
            "kitten_bed": FurnitureItem("kitten_bed", x=float(self.bounds.right - 180), y=floor - bed_h, size=bed_w),
            "toy_ball": FurnitureItem("toy_ball", x=float((self.bounds.left + self.bounds.right) // 2), y=floor - 56, size=56),
        }
        # Toy ball hidden by default until spawned
        self.furniture["toy_ball"].is_active = False

    def update_bounds(self, new_bounds: ScreenBounds) -> None:
        self.bounds = new_bounds
        for pet in (self.puppy, self.kitten):
            pet.floor_y = float(self.bounds.bottom - pet.pet_size)
            pet.x = self.bounds.clamp_x(pet.x, pet.pet_size)
            if not pet.is_dragging:
                pet.y = min(pet.floor_y, max(float(self.bounds.top), pet.y))

        for item in self.furniture.values():
            item.x = self.bounds.clamp_x(item.x, item.size)
            if not item.is_dragging:
                item.y = min(float(self.bounds.bottom - item.size), max(float(self.bounds.top), item.y))

    def toggle_follow_cursor(self, enable: Optional[bool] = None) -> bool:
        if enable is None:
            self.follow_cursor = not self.follow_cursor
        else:
            self.follow_cursor = bool(enable)
        if self.follow_cursor:
            for pet in (self.puppy, self.kitten):
                if pet.state in ("SLEEP", "EAT"):
                    pet.set_state("WALK")
                pet.is_eating_at_bowl = False
                pet.is_sleeping_in_bed = False
                pet.target_furniture = None
                pet.lock_eating_timer = 0.0
                pet.lock_sleep_timer = 0.0
                pet.busy_timer = 99999.0
        else:
            for pet in (self.puppy, self.kitten):
                pet.busy_timer = 0.0
        return self.follow_cursor

    def send_to_bed(self, pet_name: str) -> None:
        self.follow_cursor = False
        pet = self.puppy if pet_name == "puppy" else self.kitten
        target_bed = "puppy_bed" if pet_name == "puppy" else "kitten_bed"
        if not self.furniture[target_bed].is_active:
            self.furniture[target_bed].is_active = True
        pet.target_furniture = target_bed
        pet.lock_sleep_timer = 99999.0
        pet.lock_eating_timer = 0.0
        pet.busy_timer = 99999.0
        pet.set_state("WALK")

    def send_to_bowl(self, pet_name: str) -> None:
        self.follow_cursor = False
        pet = self.puppy if pet_name == "puppy" else self.kitten
        target_bowl = "puppy_bowl" if pet_name == "puppy" else "kitten_bowl"
        if not self.furniture[target_bowl].is_active:
            self.furniture[target_bowl].is_active = True
        pet.target_furniture = target_bowl
        pet.lock_eating_timer = 40.0
        pet.lock_sleep_timer = 0.0
        pet.busy_timer = 40.0
        pet.set_state("WALK")

    def call_both_to_eat(self) -> None:
        """Both pets head to their respective food bowls and feast undisturbed."""
        self.follow_cursor = False
        for b_name in ("puppy_bowl", "kitten_bowl"):
            if not self.furniture[b_name].is_active:
                self.furniture[b_name].is_active = True
        for pet_name in ("puppy", "kitten"):
            pet = self.puppy if pet_name == "puppy" else self.kitten
            pet.snuggle_timer = 0.0
            pet.is_sleeping_in_bed = False
            pet.lock_sleep_timer = 0.0
            pet.target_furniture = "puppy_bowl" if pet_name == "puppy" else "kitten_bowl"
            pet.lock_eating_timer = 40.0
            pet.busy_timer = 40.0
            pet.set_state("WALK")
            pet.vy = -4.0  # Joyful hop towards food

    def bedtime_for_both(self) -> None:
        """Both pets trot to their beds and sleep undisturbed."""
        self.follow_cursor = False
        for b_name in ("puppy_bed", "kitten_bed"):
            if not self.furniture[b_name].is_active:
                self.furniture[b_name].is_active = True
        for pet_name in ("puppy", "kitten"):
            pet = self.puppy if pet_name == "puppy" else self.kitten
            pet.snuggle_timer = 0.0
            pet.is_eating_at_bowl = False
            pet.lock_eating_timer = 0.0
            pet.target_furniture = "puppy_bed" if pet_name == "puppy" else "kitten_bed"
            pet.lock_sleep_timer = 99999.0
            pet.busy_timer = 99999.0
            pet.set_state("WALK")

    def wake_up_both(self) -> None:
        """Wakes both pets from bed/bowls into active happy play roaming."""
        self.follow_cursor = False
        for pet in (self.puppy, self.kitten):
            pet.target_furniture = None
            pet.is_sleeping_in_bed = False
            pet.is_eating_at_bowl = False
            pet.lock_sleep_timer = 0.0
            pet.lock_eating_timer = 0.0
            pet.busy_timer = 0.0
            pet.set_state("PLAY")
            pet.vy = -5.0  # Big joyful wake-up bounce

    def both_snuggle(self) -> None:
        """Triggers snuggle cuddle mode on both pets simultaneously."""
        self.follow_cursor = False
        for pet in (self.puppy, self.kitten):
            pet.trigger_snuggle()

    def toggle_toy_ball(self, enable: Optional[bool] = None) -> bool:
        ball = self.furniture["toy_ball"]
        if enable is None:
            ball.is_active = not ball.is_active
        else:
            ball.is_active = bool(enable)
        if ball.is_active:
            ball.x = float((self.bounds.left + self.bounds.right) // 2)
            ball.y = float(self.bounds.bottom - ball.size - 140)
            ball.vy = -9.5
            ball.vx = random.choice([-5.5, 5.5])
        else:
            ball.vx = 0.0
            ball.vy = 0.0
        return ball.is_active

    def bounce_toy_ball(self) -> None:
        self.follow_cursor = False
        ball = self.furniture["toy_ball"]
        if not ball.is_active:
            self.toggle_toy_ball(True)
        ball.vy = -13.0  # High bouncy leap
        ball.vx = random.choice([-7.0, -5.0, 5.0, 7.0])
        # Alert both pets to play with the ball if not eating or sleeping
        for pet in (self.puppy, self.kitten):
            if pet.target_furniture is None and not pet.is_eating_at_bowl and not pet.is_sleeping_in_bed:
                pet.busy_timer = 30.0
                pet.set_state("PLAY")
                pet.vy = -4.5

    def put_away_toy_ball(self) -> None:
        ball = self.furniture["toy_ball"]
        ball.is_active = False
        ball.vx = 0.0
        ball.vy = 0.0
        for pet in (self.puppy, self.kitten):
            pet.busy_timer = 0.0
            if pet.state == "PLAY" and pet.snuggle_timer <= 0:
                pet.set_state("WALK")

    def step_physics(self) -> None:
        if self.ball_kick_cooldown > 0:
            self.ball_kick_cooldown = max(0.0, self.ball_kick_cooldown - 0.03)

        # 1. Physics for all furniture items
        for item in self.furniture.values():
            item.step_physics(self.bounds, self.gravity, self.bounce_damping)

        # 2. Physics & AI for Puppy and Kitten
        ball = self.furniture["toy_ball"]
        for pet in (self.puppy, self.kitten):
            if pet.is_dragging:
                continue

            if pet.snuggle_timer > 0:
                pet.snuggle_timer = max(0.0, pet.snuggle_timer - 0.028)
            if pet.busy_timer > 0:
                pet.busy_timer = max(0.0, pet.busy_timer - 0.03)

            # Follow Mouse Cursor
            if self.follow_cursor:
                # Puppy tracks slightly to the left (-55px), Kitten slightly to the right (+55px)
                offset_x = -55.0 if pet.name == "puppy" else 55.0
                target_cx = self.cursor_x + offset_x
                pet_cx = pet.x + pet.pet_size * 0.5
                dx = target_cx - pet_cx
                abs_dx = abs(dx)

                # Cursor height check: if cursor is high above pet floor
                cursor_high = (pet.floor_y - self.cursor_y) > 160.0

                if abs_dx > 12.0:
                    pet.direction = 1 if dx > 0 else -1
                    if pet.state != "WALK":
                        pet.set_state("WALK")
                    if abs_dx > 250.0:
                        speed = pet.walk_speed * 3.2
                    elif abs_dx > 80.0:
                        speed = pet.walk_speed * 2.2
                    else:
                        speed = pet.walk_speed * 1.4
                    step = min(abs_dx, speed) * pet.direction
                    pet.x = self.bounds.clamp_x(pet.x + step, pet.pet_size)
                else:
                    if abs(self.cursor_x - pet_cx) > 4.0:
                        pet.direction = 1 if self.cursor_x > pet_cx else -1
                    if cursor_high and pet.y >= pet.floor_y - 2 and random.random() < 0.03:
                        pet.set_state("PLAY")
                        pet.vy = -5.0
                    elif pet.state == "WALK":
                        pet.set_state("IDLE")

                self._settle_ground_gravity(pet)
                continue

            # Navigation to Furniture (Bed or Bowl)
            if pet.target_furniture is not None:
                item = self.furniture.get(pet.target_furniture)
                if not item or not item.is_active:
                    pet.target_furniture = None
                else:
                    is_bed = "bed" in pet.target_furniture
                    if is_bed:
                        target_x = self.bounds.clamp_x(item.x + (item.size - pet.pet_size) * 0.5, pet.pet_size)
                    else:
                        # Position to left or right of bowl
                        item_center = item.x + item.size * 0.5
                        pet_center = pet.x + pet.pet_size * 0.5
                        if pet_center <= item_center:
                            target_x = self.bounds.clamp_x(item.x - pet.pet_size * 0.55, pet.pet_size)
                            desired_dir = 1
                        else:
                            target_x = self.bounds.clamp_x(item.x + item.size - pet.pet_size * 0.45, pet.pet_size)
                            desired_dir = -1

                    dx = target_x - pet.x
                    max_x = float(self.bounds.right - pet.pet_size)
                    min_x = float(self.bounds.left)
                    reached_edge = (dx > 0 and pet.x >= max_x - 0.5) or (dx < 0 and pet.x <= min_x + 0.5)
                    if abs(dx) > 4.0 and not reached_edge:
                        pet.direction = 1 if dx > 0 else -1
                        if pet.state != "WALK":
                            pet.set_state("WALK")
                        step = min(abs(dx), pet.walk_speed * 1.6) * (1 if dx > 0 else -1)
                        pet.x = self.bounds.clamp_x(pet.x + step, pet.pet_size)
                        self._settle_ground_gravity(pet)
                        continue
                    else:
                        pet.x = target_x
                        pet.target_furniture = None
                        if is_bed:
                            pet.is_sleeping_in_bed = True
                            pet.y = item.y + item.size - pet.pet_size - 8
                            pet.vx, pet.vy = 0.0, 0.0
                            pet.set_state("SLEEP")
                        else:
                            pet.is_eating_at_bowl = True
                            pet.direction = desired_dir
                            pet.vx, pet.vy = 0.0, 0.0
                            pet.set_state("EAT")
                        continue

            # Active Sleeping in Bed settling
            if pet.is_sleeping_in_bed:
                bed_name = "puppy_bed" if pet.name == "puppy" else "kitten_bed"
                bed_item = self.furniture[bed_name]
                if not bed_item.is_active or pet.state != "SLEEP":
                    pet.is_sleeping_in_bed = False
                else:
                    bed_cx = self.bounds.clamp_x(bed_item.x + (bed_item.size - pet.pet_size) * 0.5, pet.pet_size)
                    bed_cushion_y = bed_item.y + bed_item.size - pet.pet_size - 8
                    if bed_item.is_dragging or abs(pet.x - bed_cx) > 35.0 or abs(pet.y - bed_cushion_y) > 25.0 or abs(bed_item.vy) > 1.0:
                        pet.is_sleeping_in_bed = False
                        pet.target_furniture = bed_name
                        pet.set_state("PLAY")
                        pet.vy = -4.0  # Woken up!
                        continue
                    else:
                        pet.x = bed_cx
                        pet.y = bed_cushion_y
                        pet.vx, pet.vy = 0.0, 0.0
                        continue

            # Active Eating at Bowl settling
            if pet.is_eating_at_bowl:
                bowl_name = "puppy_bowl" if pet.name == "puppy" else "kitten_bowl"
                bowl_item = self.furniture[bowl_name]
                if not bowl_item.is_active or pet.state != "EAT":
                    pet.is_eating_at_bowl = False
                else:
                    b_center = bowl_item.x + bowl_item.size * 0.5
                    p_center = pet.x + pet.pet_size * 0.5
                    if bowl_item.is_dragging or abs(p_center - b_center) > 85.0 or abs(bowl_item.vy) > 1.0:
                        pet.is_eating_at_bowl = False
                        pet.target_furniture = bowl_name
                        pet.set_state("PLAY")
                        pet.vy = -4.0
                        continue
                    else:
                        pet.direction = 1 if p_center < b_center else -1
                        pet.vx = 0.0
                        pet.vy = 0.0
                        pet.y = pet.floor_y
                        continue

            # Autonomous Ball Chasing
            if (
                ball.is_active
                and pet.target_furniture is None
                and not pet.is_sleeping_in_bed
                and not pet.is_eating_at_bowl
                and pet.snuggle_timer <= 0
                and not self.follow_cursor
            ):
                ball_c = ball.x + ball.size * 0.5
                pet_c = pet.x + pet.pet_size * 0.5

                # Flanking offset: puppy approaches from left (-40), kitten approaches from right (+40)
                flank_offset = -40.0 if pet.name == "puppy" else 40.0
                target_x = self.bounds.clamp_x(ball_c + flank_offset - pet.pet_size * 0.5, pet.pet_size)
                dx = target_x - pet.x
                abs_dx = abs(dx)
                dist_to_ball = abs(ball_c - pet_c)

                # If far from target position or ball is moving away, run smoothly
                if abs_dx > 14.0 or (dist_to_ball > 60.0 and abs(ball.vx) > 0.4):
                    pet.direction = 1 if dx > 0 else -1
                    if pet.state != "WALK":
                        pet.set_state("WALK")
                    run_speed = pet.walk_speed * (2.2 if dist_to_ball > 140 else 1.6)
                    step = min(abs_dx, run_speed) * (1 if dx > 0 else -1)
                    pet.x = self.bounds.clamp_x(pet.x + step, pet.pet_size)
                else:
                    # In kicking range: face ball
                    pet.direction = 1 if ball_c >= pet_c else -1
                    floor_ball_y = float(self.bounds.bottom - ball.size)
                    ball_kickable = (ball.y >= floor_ball_y - 85.0)

                    if self.ball_kick_cooldown <= 0.0 and ball_kickable:
                        self.ball_kick_cooldown = 0.65
                        pet.set_state("PLAY")
                        pet.vy = -4.8  # Joyful pounce

                        # Kick direction: toward the opposite side or center
                        kick_dir = 1 if pet.name == "puppy" else -1
                        if ball.x <= self.bounds.left + 70:
                            kick_dir = 1
                        elif ball.x >= self.bounds.right - ball.size - 70:
                            kick_dir = -1

                        ball.vy = -random.uniform(9.0, 13.0)
                        ball.vx = kick_dir * random.uniform(5.5, 9.0)
                    else:
                        if pet.y >= pet.floor_y - 2 and pet.state != "PLAY":
                            pet.set_state("PLAY")

                self._settle_ground_gravity(pet)
                continue

            # Airborne / Jumping / Gravity physics
            if not pet.is_sleeping_in_bed and (pet.y < pet.floor_y or abs(pet.vy) > 0.05 or abs(pet.vx) > 0.2):
                pet.vy += self.gravity
                pet.y += pet.vy
                pet.x += pet.vx
                pet.vx *= 0.95

                # Ceiling and screen boundary clamps
                if pet.y < self.bounds.top:
                    pet.y = float(self.bounds.top)
                    pet.vy = abs(pet.vy) * 0.3
                pet.x = self.bounds.clamp_x(pet.x, pet.pet_size)

                if pet.y >= pet.floor_y:
                    pet.y = pet.floor_y
                    if abs(pet.vy) > 3.5:
                        pet.vy = -abs(pet.vy) * self.bounce_damping
                    else:
                        pet.vy, pet.vx = 0.0, 0.0
                        if pet.state == "PLAY" and pet.snuggle_timer <= 0:
                            pet.set_state("IDLE")
                continue

            # Normal Walking & Screen Edge Bouncing
            if pet.state == "WALK":
                pet.x += pet.walk_speed * pet.direction
                min_x = float(self.bounds.left)
                max_x = float(self.bounds.right - pet.pet_size)
                if pet.x <= min_x:
                    pet.x = min_x
                    pet.direction = 1
                elif pet.x >= max_x:
                    pet.x = max_x
                    pet.direction = -1

            # Social Interaction: When Puppy and Kitten meet
            if pet.name == "puppy" and self.puppy.state == "WALK" and self.kitten.state in ("WALK", "IDLE"):
                dist = abs((self.puppy.x + self.puppy.pet_size * 0.5) - (self.kitten.x + self.kitten.pet_size * 0.5))
                if dist < 65.0 and random.random() < 0.05:
                    self.puppy.set_state("PLAY")
                    self.kitten.set_state("PLAY")
                    self.puppy.direction = 1 if self.puppy.x < self.kitten.x else -1
                    self.kitten.direction = -self.puppy.direction

            self._settle_ground_gravity(pet)

    def _settle_ground_gravity(self, pet: PetEntity) -> None:
        if pet.y < pet.floor_y or pet.vy < -0.05:
            pet.vy += self.gravity
            pet.y += pet.vy
            if pet.y >= pet.floor_y:
                pet.y = pet.floor_y
                pet.vy = 0.0
        else:
            pet.y = pet.floor_y
            pet.vy = 0.0

    def advance_frames(self) -> None:
        for pet in (self.puppy, self.kitten):
            pet.frame_index = (pet.frame_index + 1) % 4

    def pick_random_states(self, rng: random.Random = random) -> None:
        for pet in (self.puppy, self.kitten):
            # If pet is dragging, navigating, snuggling, busy with a task, or following cursor:
            if (
                pet.is_dragging
                or pet.target_furniture is not None
                or pet.snuggle_timer > 0
                or pet.busy_timer > 0
                or self.follow_cursor
            ):
                continue

            if pet.is_sleeping_in_bed:
                continue

            if pet.is_eating_at_bowl:
                if pet.lock_eating_timer > 0:
                    pet.lock_eating_timer = max(0.0, pet.lock_eating_timer - 7.0)
                    continue
                # Finished eating: happily switch to walk
                pet.is_eating_at_bowl = False
                pet.set_state("WALK")
                continue

            # Rare autonomous nap in bed (2% for kitten, 1% for puppy) - never on floor!
            if not self.furniture["toy_ball"].is_active:
                if pet.name == "kitten" and rng.random() < 0.02:
                    self.send_to_bed("kitten")
                    continue
                if pet.name == "puppy" and rng.random() < 0.01:
                    self.send_to_bed("puppy")
                    continue

            # Natural desktop pet wandering behavior (NO RANDOM SLEEP ON HARD FLOOR!)
            weights = {
                "puppy": [("WALK", 0.60), ("IDLE", 0.30), ("PLAY", 0.10)],
                "kitten": [("WALK", 0.50), ("IDLE", 0.40), ("PLAY", 0.10)],
                "dog": [("WALK", 0.60), ("IDLE", 0.30), ("PLAY", 0.10)],
                "cat": [("WALK", 0.50), ("IDLE", 0.40), ("PLAY", 0.10)],
            }
            choices, probs = zip(*weights.get(pet.name, weights.get(pet.species)))
            new_st = rng.choices(choices, weights=probs)[0]
            pet.set_state(new_st)
            if new_st == "WALK" and rng.random() < 0.5:
                pet.direction = rng.choice([-1, 1])
