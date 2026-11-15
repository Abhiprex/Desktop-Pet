"""
Core state machine and 2D physics engine for the Cozy Desktop Pet (v3).
Supports:
- 6 States: IDLE, WALK, PLAY, SLEEP, EAT, JUMP
- Interactive Toy Ball physics (gravity, bounce, and autonomous pet chasing)
- Hop/Jump physics impulse and snack feeding timer
"""
import random
import math
from dataclasses import dataclass
from typing import Dict, List, Optional

VALID_STATES = ("IDLE", "WALK", "PLAY", "SLEEP", "EAT", "JUMP")


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


class PetEngine:
    def __init__(
        self,
        bounds: ScreenBounds,
        pet_size: int = 112,
        walk_speed: float = 2.5,
        chase_speed: float = 4.2,
        gravity: float = 1.15,
        bounce_damping: float = 0.28,
    ):
        if pet_size <= 0:
            raise ValueError("pet_size must be positive")
        self.bounds = bounds
        self.pet_size = pet_size
        self.walk_speed = walk_speed
        self.chase_speed = chase_speed
        self.gravity = gravity
        self.bounce_damping = bounce_damping

        self.state: str = "WALK"
        self.frame_index: int = 0
        self.direction: int = 1
        self.is_dragging: bool = False

        self.floor_y: float = float(self.bounds.bottom - self.pet_size)
        self.x: float = float((self.bounds.left + self.bounds.right - self.pet_size) // 2)
        self.y: float = self.floor_y
        self.vx: float = 0.0
        self.vy: float = 0.0
        self.flight_timer: float = 0.0
        self.flying_mode: bool = False
        self.target_flight_y: float = float(self.floor_y * 0.45)

        # Interactive Toy Ball coordinates (None when hidden)
        self.toy_active: bool = False
        self.toy_size: int = 56
        self.toy_x: float = 0.0
        self.toy_y: float = 0.0
        self.toy_vx: float = 0.0
        self.toy_vy: float = 0.0
        self.toy_dragging: bool = False

        # Permanent Bed state
        self.bed_active: bool = False
        self.bed_size: int = 96
        self.bed_x: float = float(self.bounds.right - 240)
        self.bed_y: float = float(self.bounds.bottom - 96)
        self.bed_vx: float = 0.0
        self.bed_vy: float = 0.0
        self.bed_dragging: bool = False

        # Permanent Food Bowl state
        self.bowl_active: bool = False
        self.bowl_size: int = 76
        self.bowl_x: float = float(self.bounds.right - 340)
        self.bowl_y: float = float(self.bounds.bottom - 76)
        self.bowl_vx: float = 0.0
        self.bowl_vy: float = 0.0
        self.bowl_dragging: bool = False

        self.target_action: Optional[str] = None
        self.is_eating_at_bowl: bool = False
        self.is_sleeping_in_bed: bool = False

        self.follow_cursor: bool = False
        self.cursor_x: float = 0.0
        self.cursor_y: float = 0.0
        self.snuggle_timer: float = 0.0

        self.frame_counts: Dict[str, int] = {s: 4 for s in VALID_STATES}

    @property
    def toy_floor_y(self) -> float:
        return float(self.bounds.bottom - self.toy_size)

    @property
    def bed_floor_y(self) -> float:
        return float(self.bounds.bottom - self.bed_size)

    @property
    def bowl_floor_y(self) -> float:
        return float(self.bounds.bottom - self.bowl_size)

    def update_bounds(self, new_bounds: ScreenBounds) -> None:
        self.bounds = new_bounds
        self.floor_y = float(self.bounds.bottom - self.pet_size)
        self.x = self.bounds.clamp_x(self.x, self.pet_size)
        if not self.is_dragging:
            if not self.flying_mode:
                self.y = min(self.floor_y, max(float(self.bounds.top), self.y))
            else:
                self.y = min(self.floor_y - 20, max(float(self.bounds.top + 20), self.y))
        if self.toy_active:
            self.toy_x = self.bounds.clamp_x(self.toy_x, self.toy_size)
            if not self.toy_dragging:
                self.toy_y = min(self.toy_floor_y, max(float(self.bounds.top), self.toy_y))
        if self.bed_active:
            self.bed_x = self.bounds.clamp_x(self.bed_x, self.bed_size)
            if not self.bed_dragging:
                self.bed_y = min(self.bed_floor_y, max(float(self.bounds.top), self.bed_y))
        if self.bowl_active:
            self.bowl_x = self.bounds.clamp_x(self.bowl_x, self.bowl_size)
            if not self.bowl_dragging:
                self.bowl_y = min(self.bowl_floor_y, max(float(self.bounds.top), self.bowl_y))

    def toggle_bed(self, enable: Optional[bool] = None) -> bool:
        """Toggle or set permanent bed visibility."""
        if enable is None:
            self.bed_active = not self.bed_active
        else:
            self.bed_active = bool(enable)
        if not self.bed_active:
            if self.target_action == "NAP_BED":
                self.target_action = None
            if self.is_sleeping_in_bed:
                self.is_sleeping_in_bed = False
                self.y = self.floor_y
                self.set_state("IDLE")
        return self.bed_active

    def toggle_bowl(self, enable: Optional[bool] = None) -> bool:
        """Toggle or set permanent food bowl visibility."""
        if enable is None:
            self.bowl_active = not self.bowl_active
        else:
            self.bowl_active = bool(enable)
        if not self.bowl_active:
            if self.target_action == "EAT_BOWL":
                self.target_action = None
            if self.is_eating_at_bowl:
                self.is_eating_at_bowl = False
                self.set_state("IDLE")
        return self.bowl_active

    def on_bed_moved(self) -> None:
        """Called when bed position is moved/dragged. If pet is sleeping in it, startle and chase!"""
        if self.is_sleeping_in_bed:
            self.is_sleeping_in_bed = False
            self.target_action = "NAP_BED"
            self.set_state("JUMP")
            self.vy = -4.0

    def on_bowl_moved(self) -> None:
        """Called when bowl position is moved/dragged. If pet is eating from it, startle and chase!"""
        if self.is_eating_at_bowl:
            self.is_eating_at_bowl = False
            self.target_action = "EAT_BOWL"
            self.set_state("JUMP")
            self.vy = -4.5

    def go_to_bed(self) -> None:
        """Guide the pet to walk to its bed and settle down for a nap."""
        if not self.bed_active:
            self.toggle_bed(True)
        self.flying_mode = False
        self.target_action = "NAP_BED"
        self.set_state("WALK")

    def go_to_bowl(self) -> None:
        """Guide the pet to walk to its food bowl and eat."""
        if not self.bowl_active:
            self.toggle_bowl(True)
        self.flying_mode = False
        self.target_action = "EAT_BOWL"
        self.set_state("WALK")

    def toggle_flying(self, enable: Optional[bool] = None) -> bool:
        """Toggle or set continuous 2D flight mode across the screen."""
        if enable is None:
            self.flying_mode = not self.flying_mode
        else:
            self.flying_mode = bool(enable)

        if self.flying_mode:
            self.set_state("JUMP")
            self.flight_timer = 0.0
            # Target middle/upper desktop height
            self.target_flight_y = float(self.bounds.top + (self.bounds.bottom - self.bounds.top) * 0.4)
            self.vy = -6.0
        else:
            self.target_flight_y = self.floor_y
            self.y = self.floor_y
            self.vy = 0.0
            self.set_state("WALK")
        return self.flying_mode

    def toggle_follow_cursor(self, enable: Optional[bool] = None) -> bool:
        """Toggle or explicitly set cursor following mode."""
        if enable is None:
            self.follow_cursor = not self.follow_cursor
        else:
            self.follow_cursor = bool(enable)
        if self.follow_cursor:
            if self.state in ("SLEEP", "EAT"):
                self.set_state("WALK")
            self.is_eating_at_bowl = False
            self.is_sleeping_in_bed = False
            self.target_action = None
        return self.follow_cursor

    def trigger_snuggle(self) -> None:
        """Trigger a loving, snuggly cuddle reaction with happy animation."""
        self.flying_mode = False
        self.is_eating_at_bowl = False
        self.is_sleeping_in_bed = False
        self.target_action = None
        self.set_state("PLAY")
        self.snuggle_timer = 4.0
        if self.y >= self.floor_y - 2:
            self.vy = -4.5  # Joyful little hop into a cuddle

    def set_state(self, new_state: str) -> None:
        if new_state not in VALID_STATES:
            raise ValueError(f"Invalid state '{new_state}'. Must be one of {VALID_STATES}")
        if new_state != "EAT":
            self.is_eating_at_bowl = False
        if new_state != "SLEEP":
            self.is_sleeping_in_bed = False
        self.state = new_state
        self.frame_index = 0

    def trigger_jump(self) -> None:
        """Give the pet a joyful upward hop impulse."""
        if self.is_dragging:
            return
        self.set_state("JUMP")
        self.vy = -11.5
        self.vx = 2.8 * self.direction

    def feed_snack(self) -> None:
        """Feed the pet a cookie snack."""
        if self.is_dragging:
            return
        self.vx = 0.0
        self.set_state("EAT")

    def spawn_toy(self, target_x: Optional[float] = None, target_y: Optional[float] = None) -> None:
        """Spawn a separate bouncing toy ball on the screen for the pet to chase."""
        self.toy_active = True
        if target_x is None:
            offset = 180 * self.direction
            candidate = self.x + offset
            if candidate < self.bounds.left + 40 or candidate > self.bounds.right - self.toy_size - 40:
                candidate = (self.bounds.left + self.bounds.right) / 2.0
            self.toy_x = self.bounds.clamp_x(candidate, self.toy_size)
        else:
            self.toy_x = self.bounds.clamp_x(target_x, self.toy_size)

        if target_y is None:
            self.toy_y = max(float(self.bounds.top + 40), self.floor_y - 160.0)
        else:
            self.toy_y = self.bounds.clamp_y(target_y, self.toy_size)

        self.toy_vx = random.choice([-4.0, 4.0])
        self.toy_vy = -4.0
        if self.state == "SLEEP":
            self.set_state("WALK")

    def despawn_toy(self) -> None:
        self.toy_active = False
        self.toy_dragging = False
        if self.state == "PLAY":
            self.set_state("IDLE")

    def bounce_toy(self, impulse_x: Optional[float] = None, impulse_y: float = -8.5) -> None:
        """Give the toy ball a fun physical bounce/kick."""
        if not self.toy_active:
            self.spawn_toy()
        self.toy_vy = impulse_y
        if impulse_x is None:
            self.toy_vx = random.choice([-5.0, 5.0])
        else:
            self.toy_vx = impulse_x
        if self.state == "SLEEP":
            self.set_state("WALK")

    def advance_frame(self) -> int:
        total = self.frame_counts.get(self.state, 1)
        self.frame_index = (self.frame_index + 1) % max(1, total)
        return self.frame_index

    def pick_next_state(self, rng: random.Random = random) -> str:
        if self.is_dragging or (not self.flying_mode and self.y < self.floor_y):
            return self.state

        if self.follow_cursor or self.snuggle_timer > 0:
            return self.state

        if self.target_action is not None:
            # Currently navigating to bed or bowl, let it finish arriving
            return self.state

        if self.flying_mode:
            # While in flight mode, stay 100% in soaring & wing-flapping flight animation
            self.set_state("JUMP")
            if rng.random() < 0.35:
                self.direction = rng.choice([-1, 1])
            return self.state

        if self.toy_active:
            # While the toy ball is out, stay active chasing/playing with it
            dist = abs((self.x + self.pet_size * 0.5) - (self.toy_x + self.toy_size * 0.5))
            if dist <= 50.0:
                if self.state != "PLAY":
                    self.set_state("PLAY")
            else:
                if self.state != "WALK":
                    self.set_state("WALK")
            return self.state

        if self.state == "SLEEP":
            threshold = 0.75 if self.bed_active else 0.45
            if rng.random() < threshold:
                return self.state

        weights: List[str] = ["WALK", "WALK", "IDLE", "IDLE", "PLAY", "SLEEP", "JUMP", "EAT"]
        chosen = rng.choice(weights)
        if chosen == "JUMP":
            self.trigger_jump()
        elif chosen == "SLEEP" and self.bed_active:
            self.go_to_bed()
        elif chosen == "EAT" and self.bowl_active:
            self.go_to_bowl()
        else:
            self.set_state(chosen)
            if chosen == "WALK":
                self.direction = rng.choice([-1, 1])
        return self.state

    def start_drag(self) -> None:
        self.is_dragging = True
        self.target_action = None
        self.is_eating_at_bowl = False
        self.is_sleeping_in_bed = False
        self.vx = 0.0
        self.vy = 0.0
        if not self.flying_mode:
            self.set_state("IDLE")
        else:
            self.set_state("JUMP")

    def drag_to(self, new_x: float, new_y: float) -> None:
        if not self.is_dragging:
            return
        clamped_x = self.bounds.clamp_x(new_x, self.pet_size)
        clamped_y = self.bounds.clamp_y(new_y, self.pet_size)
        self.vx = (clamped_x - self.x) * 0.45
        self.vy = (clamped_y - self.y) * 0.35
        self.x = clamped_x
        self.y = clamped_y

    def end_drag(self) -> None:
        self.is_dragging = False
        self.vx = max(-14.0, min(14.0, self.vx))
        self.vy = max(-12.0, min(12.0, self.vy))
        if self.flying_mode:
            self.target_flight_y = self.bounds.clamp_y(self.y, self.pet_size)
            self.set_state("JUMP")
            self.vy = 0.0
        elif self.y < self.floor_y:
            self.set_state("JUMP")

    def step_toy_physics(self) -> None:
        if not self.toy_active or self.toy_dragging:
            return
        t_floor = self.toy_floor_y
        if self.toy_y < t_floor or abs(self.toy_vy) > 0.1 or abs(self.toy_vx) > 0.15:
            self.toy_vy += self.gravity * 0.9
            self.toy_y += self.toy_vy
            self.toy_x += self.toy_vx
            self.toy_vx *= 0.98

            # Side boundary bounces
            max_tx = self.bounds.right - self.toy_size
            if self.toy_x <= self.bounds.left:
                self.toy_x = float(self.bounds.left)
                self.toy_vx = abs(self.toy_vx) * 0.75
            elif self.toy_x >= max_tx:
                self.toy_x = float(max_tx)
                self.toy_vx = -abs(self.toy_vx) * 0.75

            # Ceiling boundary bounce
            if self.toy_y < self.bounds.top:
                self.toy_y = float(self.bounds.top)
                self.toy_vy = abs(self.toy_vy) * 0.6

            # Floor settlement and bounce
            if self.toy_y >= t_floor:
                self.toy_y = t_floor
                if abs(self.toy_vy) > 2.0:
                    self.toy_vy = -abs(self.toy_vy) * 0.58
                else:
                    self.toy_vy = 0.0
                    self.toy_vx *= 0.85
                    if abs(self.toy_vx) < 0.15:
                        self.toy_vx = 0.0

    def step_bed_physics(self) -> None:
        """Gravity, falling, and landing physics for the cozy pet bed."""
        if not self.bed_active or self.bed_dragging:
            return
        b_floor = self.bed_floor_y
        if self.bed_y < b_floor or abs(self.bed_vy) > 0.1 or abs(self.bed_vx) > 0.15:
            self.bed_vy += self.gravity * 1.1
            self.bed_y += self.bed_vy
            self.bed_x += self.bed_vx
            self.bed_vx *= 0.95

            # Side boundary bounds
            max_bx = self.bounds.right - self.bed_size
            if self.bed_x <= self.bounds.left:
                self.bed_x = float(self.bounds.left)
                self.bed_vx = abs(self.bed_vx) * 0.4
            elif self.bed_x >= max_bx:
                self.bed_x = float(max_bx)
                self.bed_vx = -abs(self.bed_vx) * 0.4

            # Ceiling clamp
            if self.bed_y < self.bounds.top:
                self.bed_y = float(self.bounds.top)
                self.bed_vy = abs(self.bed_vy) * 0.3

            # Floor settlement (plush cushion landing)
            if self.bed_y >= b_floor:
                self.bed_y = b_floor
                if abs(self.bed_vy) > 2.5:
                    self.bed_vy = -abs(self.bed_vy) * 0.22
                else:
                    self.bed_vy = 0.0
                    self.bed_vx = 0.0

    def step_bowl_physics(self) -> None:
        """Gravity, falling, and landing physics for the snack food bowl."""
        if not self.bowl_active or self.bowl_dragging:
            return
        b_floor = self.bowl_floor_y
        if self.bowl_y < b_floor or abs(self.bowl_vy) > 0.1 or abs(self.bowl_vx) > 0.15:
            self.bowl_vy += self.gravity * 1.2
            self.bowl_y += self.bowl_vy
            self.bowl_x += self.bowl_vx
            self.bowl_vx *= 0.96

            # Side boundary bounds
            max_bx = self.bounds.right - self.bowl_size
            if self.bowl_x <= self.bounds.left:
                self.bowl_x = float(self.bounds.left)
                self.bowl_vx = abs(self.bowl_vx) * 0.5
            elif self.bowl_x >= max_bx:
                self.bowl_x = float(max_bx)
                self.bowl_vx = -abs(self.bowl_vx) * 0.5

            # Ceiling clamp
            if self.bowl_y < self.bounds.top:
                self.bowl_y = float(self.bounds.top)
                self.bowl_vy = abs(self.bowl_vy) * 0.3

            # Floor settlement (ceramic bowl landing)
            if self.bowl_y >= b_floor:
                self.bowl_y = b_floor
                if abs(self.bowl_vy) > 2.5:
                    self.bowl_vy = -abs(self.bowl_vy) * 0.28
                else:
                    self.bowl_vy = 0.0
                    self.bowl_vx = 0.0

    def step_physics(self) -> None:
        self.step_toy_physics()
        self.step_bed_physics()
        self.step_bowl_physics()

        if self.is_dragging:
            return

        if self.snuggle_timer > 0:
            self.snuggle_timer = max(0.0, self.snuggle_timer - 0.028)

        # Follow Mouse Cursor Mode
        if self.follow_cursor:
            if self.flying_mode:
                # Aerial follow: smoothly glide alongside cursor in 2D
                target_x = self.bounds.clamp_x(self.cursor_x - self.pet_size * 0.5, self.pet_size)
                target_y = self.bounds.clamp_y(self.cursor_y - self.pet_size * 0.5 - 15.0, self.pet_size)
                dx = target_x - self.x
                dy = target_y - self.y
                if abs(dx) > 15.0:
                    self.direction = 1 if dx > 0 else -1
                self.x = self.bounds.clamp_x(self.x + max(-6.5, min(6.5, dx * 0.12)), self.pet_size)
                self.y = self.bounds.clamp_y(self.y + max(-6.5, min(6.5, dy * 0.12)), self.pet_size)
                self.state = "JUMP"
                return
            else:
                # Ground follow: walk toward cursor_x and stop near it
                pet_center = self.x + self.pet_size * 0.5
                dx = self.cursor_x - pet_center
                if abs(dx) > 35.0:
                    self.direction = 1 if dx > 0 else -1
                    if self.state != "WALK":
                        self.set_state("WALK")
                    step = min(abs(dx), self.walk_speed * 1.8) * self.direction
                    self.x = self.bounds.clamp_x(self.x + step, self.pet_size)
                else:
                    if abs(dx) > 8.0:
                        self.direction = 1 if dx > 0 else -1
                    if self.state == "WALK":
                        self.set_state("IDLE")

                if self.y < self.floor_y:
                    self.vy += self.gravity
                    self.y += self.vy
                    if self.y >= self.floor_y:
                        self.y = self.floor_y
                        self.vy = 0.0
                else:
                    self.y = self.floor_y
                    self.vy = 0.0
                return

        # Target action navigation: Walk directly to bed or food bowl!
        if self.target_action == "NAP_BED":
            if not self.bed_active:
                self.target_action = None
            else:
                self.flying_mode = False
                bed_target_x = self.bounds.clamp_x(self.bed_x + (self.bed_size - self.pet_size) * 0.5, self.pet_size)
                dx = bed_target_x - self.x
                max_x = float(self.bounds.right - self.pet_size)
                min_x = float(self.bounds.left)
                reached_edge = (dx > 0 and self.x >= max_x - 0.5) or (dx < 0 and self.x <= min_x + 0.5)
                if abs(dx) > 4.0 and not reached_edge:
                    self.direction = 1 if dx > 0 else -1
                    if self.state != "WALK":
                        self.set_state("WALK")
                    step_x = min(abs(dx), self.walk_speed * 1.6) * (1 if dx > 0 else -1)
                    self.x = self.bounds.clamp_x(self.x + step_x, self.pet_size)
                    return
                else:
                    self.x = bed_target_x
                    self.target_action = None
                    self.is_sleeping_in_bed = True
                    self.y = self.bed_y + self.bed_size - self.pet_size - 8
                    self.vx = 0.0
                    self.vy = 0.0
                    self.set_state("SLEEP")
                    return

        if self.target_action == "EAT_BOWL":
            if not self.bowl_active:
                self.target_action = None
            else:
                self.flying_mode = False
                bowl_center = self.bowl_x + self.bowl_size * 0.5
                pet_center = self.x + self.pet_size * 0.5
                if pet_center <= bowl_center:
                    target_x = self.bounds.clamp_x(self.bowl_x - self.pet_size * 0.55, self.pet_size)
                    desired_dir = 1
                else:
                    target_x = self.bounds.clamp_x(self.bowl_x + self.bowl_size - self.pet_size * 0.45, self.pet_size)
                    desired_dir = -1
                dx = target_x - self.x
                max_x = float(self.bounds.right - self.pet_size)
                min_x = float(self.bounds.left)
                reached_edge = (dx > 0 and self.x >= max_x - 0.5) or (dx < 0 and self.x <= min_x + 0.5)
                if abs(dx) > 4.0 and not reached_edge:
                    self.direction = 1 if dx > 0 else -1
                    if self.state != "WALK":
                        self.set_state("WALK")
                    step_x = min(abs(dx), self.walk_speed * 1.6) * (1 if dx > 0 else -1)
                    self.x = self.bounds.clamp_x(self.x + step_x, self.pet_size)
                    return
                else:
                    self.x = target_x
                    self.direction = desired_dir
                    self.target_action = None
                    self.is_eating_at_bowl = True
                    self.set_state("EAT")
                    return

        # Active Sleeping in Bed handling: stay nestled, or react if bed is moved
        if self.is_sleeping_in_bed:
            if not self.bed_active or self.state != "SLEEP" or self.flying_mode:
                self.is_sleeping_in_bed = False
            else:
                bed_center_x = self.bounds.clamp_x(self.bed_x + (self.bed_size - self.pet_size) * 0.5, self.pet_size)
                bed_cushion_y = self.bed_y + self.bed_size - self.pet_size - 8
                if self.bed_dragging or abs(self.x - bed_center_x) > 35.0 or abs(self.y - bed_cushion_y) > 25.0 or abs(self.bed_vy) > 1.0:
                    self.is_sleeping_in_bed = False
                    self.target_action = "NAP_BED"
                    self.set_state("JUMP")
                    self.vy = -4.0
                    return
                else:
                    self.x = bed_center_x
                    self.y = bed_cushion_y
                    self.vx = 0.0
                    self.vy = 0.0
                    return

        # Active Eating at Bowl handling: stay eating, or react if bowl is moved
        if self.is_eating_at_bowl:
            if not self.bowl_active or self.state != "EAT" or self.flying_mode:
                self.is_eating_at_bowl = False
            else:
                bowl_center = self.bowl_x + self.bowl_size * 0.5
                pet_center = self.x + self.pet_size * 0.5
                if self.bowl_dragging or abs(pet_center - bowl_center) > 85.0 or abs(self.bowl_vy) > 1.0:
                    self.is_eating_at_bowl = False
                    self.target_action = "EAT_BOWL"
                    self.set_state("JUMP")
                    self.vy = -4.5
                    return
                else:
                    self.direction = 1 if pet_center < bowl_center else -1

        # 1. Continuous Flying Mode (soaring freely across the 2D desktop screen)
        if self.flying_mode:
            self.flight_timer += 0.045
            self.state = "JUMP"  # Always display true soaring & wing-flapping flight animation!

            # Periodically choose a new flight altitude target to explore
            if random.random() < 0.008:
                min_y = float(self.bounds.top + 40)
                max_y = float(self.floor_y - 80)
                if min_y < max_y:
                    self.target_flight_y = random.uniform(min_y, max_y)

            # Smooth horizontal soaring
            fly_speed = self.walk_speed * 1.3
            self.x += fly_speed * self.direction

            # Screen horizontal boundary turnarounds
            min_x = float(self.bounds.left)
            max_x = float(self.bounds.right - self.pet_size)
            if self.x <= min_x:
                self.x = min_x
                self.direction = 1
            elif self.x >= max_x:
                self.x = max_x
                self.direction = -1

            # Vertical gentle soaring wave + altitude tracking
            soar_wave = math.sin(self.flight_timer * 1.4) * 1.5
            diff_y = self.target_flight_y - self.y
            self.vy = soar_wave + diff_y * 0.035
            self.vy = max(-5.0, min(5.0, self.vy))
            self.y += self.vy

            # Screen vertical bounds
            min_flight_y = float(self.bounds.top + 20)
            max_flight_y = float(self.floor_y - 20)
            if self.y < min_flight_y:
                self.y = min_flight_y
                self.vy = 1.0
            elif self.y > max_flight_y:
                self.y = max_flight_y
                self.vy = -1.0

            # If chasing toy while in flight, swoop down toward it
            if self.toy_active and self.state not in ("SLEEP", "EAT"):
                toy_center = self.toy_x + self.toy_size * 0.5
                pet_center = self.x + self.pet_size * 0.5
                dx = toy_center - pet_center
                if abs(dx) > 40.0:
                    self.direction = 1 if dx > 0 else -1
                self.target_flight_y = max(float(self.bounds.top + 40), self.toy_y - 20)

            self.state = "JUMP"
            return

        # 2. Airborne / Jumping / Falling (Ground mode)
        if not self.is_sleeping_in_bed and (self.y < self.floor_y or abs(self.vy) > 0.05 or abs(self.vx) > 0.2):
            if self.y < self.floor_y or self.vy < 0:
                self.vy += self.gravity
                self.y += self.vy
                self.x += self.vx
                self.vx *= 0.95

                # Ceiling bounce/bonk
                if self.y < self.bounds.top:
                    self.y = float(self.bounds.top)
                    self.vy = abs(self.vy) * 0.4

                max_x = self.bounds.right - self.pet_size
                if self.x <= self.bounds.left:
                    self.x = float(self.bounds.left)
                    self.vx = abs(self.vx) * 0.6
                    self.direction = 1
                elif self.x >= max_x:
                    self.x = float(max_x)
                    self.vx = -abs(self.vx) * 0.6
                    self.direction = -1

                if self.y >= self.floor_y:
                    self.y = self.floor_y
                    if abs(self.vy) > 3.5:
                        self.vy = -abs(self.vy) * self.bounce_damping
                    else:
                        self.vy = 0.0
                        self.vx = 0.0
                        if self.state == "JUMP":
                            self.set_state("IDLE")
                return
            else:
                self.y = self.floor_y
                self.vy = 0.0
                self.vx = 0.0
                if self.state == "JUMP":
                    self.set_state("IDLE")

        # 2. Autonomous Toy Chasing when toy ball is active on screen
        if self.toy_active and self.state not in ("SLEEP", "EAT"):
            pet_center = self.x + self.pet_size * 0.5
            toy_center = self.toy_x + self.toy_size * 0.5
            dx = toy_center - pet_center
            if abs(dx) > 50.0:
                self.direction = 1 if dx > 0 else -1
                if self.state != "WALK":
                    self.set_state("WALK")
                self.x = self.bounds.clamp_x(self.x + self.chase_speed * self.direction, self.pet_size)
                remaining_dx = toy_center - (self.x + self.pet_size * 0.5)
                if abs(remaining_dx) <= 50.0 and self.state != "PLAY":
                    self.direction = 1 if remaining_dx >= 0 else -1
                    self.set_state("PLAY")
            else:
                # Reached the ball! Always face toward the ball
                self.direction = 1 if dx >= 0 else -1
                if self.state != "PLAY":
                    self.set_state("PLAY")
                if abs(self.toy_vx) < 0.5 and abs(self.toy_vy) < 0.5 and random.random() < 0.06:
                    self.toy_vy = -5.5
                    self.toy_vx = self.direction * 3.5
            return

        # 3. Flying & Hovering
        if self.state == "WALK":
            self.x += self.walk_speed * self.direction
            max_x = self.bounds.right - self.pet_size
            if self.x <= self.bounds.left:
                self.x = float(self.bounds.left)
                self.direction = 1
            elif self.x >= max_x:
                self.x = float(max_x)
                self.direction = -1

        # 4. Keep pet settled inside Bed while Sleeping, or facing Bowl while Eating
        if self.bed_active and self.state == "SLEEP" and not self.flying_mode:
            bed_target_x = self.bed_x + (self.bed_size - self.pet_size) * 0.5
            if abs(self.x - bed_target_x) < 35.0:
                self.x = bed_target_x
                self.y = self.bed_y + self.bed_size - self.pet_size - 8
                self.is_sleeping_in_bed = True

        if self.bowl_active and self.state == "EAT" and not self.flying_mode:
            bowl_center = self.bowl_x + self.bowl_size * 0.5
            pet_center = self.x + self.pet_size * 0.5
            if abs(pet_center - bowl_center) < 75.0:
                self.direction = 1 if pet_center < bowl_center else -1
                self.is_eating_at_bowl = True
