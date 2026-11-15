"""
Puppy & Cat Desktop Pets - Main Application (PyQt6)
Dual-pet interactive desktop overlay featuring:
- Puppy 🐶 and Kitten 🐱 with distinct animations & AI personalities.
- 4 Dedicated Interactive Furniture Items:
  * Puppy Bed & Bowl
  * Kitten Bed & Bowl
  * Play Toy Ball
- Physics gravity, floor settlement, cursor following, snuggle cuddles, and floating hearts.
"""

import sys
import os
import math
import random
from typing import Dict, Optional, List

from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, pyqtSignal, QSize
from PyQt6.QtGui import (
    QAction,
    QColor,
    QCursor,
    QFont,
    QGuiApplication,
    QIcon,
    QImage,
    QMouseEvent,
    QPainter,
    QPixmap,
)
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

from pet_engine import FurnitureItem, MultiPetEngine, PetEntity, ScreenBounds

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")


def get_screen_bounds() -> ScreenBounds:
    screen = QGuiApplication.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        return ScreenBounds(geo.left(), geo.top(), geo.right(), geo.bottom())
    return ScreenBounds(0, 0, 1920, 1040)


class FloatingHeart(QWidget):
    """Floating heart or sparkle particle on snuggle cuddles."""

    def __init__(self, x: int, y: int, char: str = "💖", parent: Optional[QWidget] = None):
        super().__init__(parent)
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        if sys.platform == "darwin":
            flags |= Qt.WindowType.SubWindow
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        else:
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        self.char = char
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vy = -random.uniform(1.6, 3.2)
        self.vx = random.uniform(-1.0, 1.0)
        self.phase = random.uniform(0, 6.28)
        self.opacity = 1.0
        self.size = random.randint(22, 30)

        self.resize(44, 44)
        self.move(int(self.pos_x - 22), int(self.pos_y - 22))
        self.show()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.start(35)

    def _step(self) -> None:
        self.opacity -= 0.038
        if self.opacity <= 0.05:
            self.timer.stop()
            self.hide()
            self.deleteLater()
            return
        self.pos_y += self.vy
        self.pos_x += self.vx + math.sin(self.phase) * 0.8
        self.phase += 0.18
        self.move(int(self.pos_x - 22), int(self.pos_y - 22))
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(max(0.0, min(1.0, self.opacity)))
        font = QFont("Segoe UI Emoji", int(self.size * 0.6))
        if not font.exactMatch():
            font = QFont("Apple Color Emoji", int(self.size * 0.6))
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.char)
        p.end()


class FurnitureWidget(QWidget):
    """Draggable physical desktop furniture item."""

    double_clicked = pyqtSignal(str)

    def __init__(
        self,
        item_name: str,
        item: FurnitureItem,
        app_controller: "DesktopPetApp",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.item_name = item_name
        self.item = item
        self.app_ctrl = app_controller
        self.drag_offset = QPoint()
        self.pixmap: Optional[QPixmap] = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self._load_pixmap()
        self.resize(self.item.size, self.item.size)
        self.move(int(self.item.x), int(self.item.y))

        tooltip_map = {
            "puppy_bed": "Puppy Bed 🛏️ (Double-click to send Puppy to sleep!)",
            "kitten_bed": "Kitten Bed 🛏️ (Double-click to send Kitten to sleep!)",
            "puppy_bowl": "Puppy Bowl 🥣 (Double-click to feed Puppy!)",
            "kitten_bowl": "Kitten Bowl 🥣 (Double-click to feed Kitten!)",
            "toy_ball": "Toy Ball ⚽ (Click or bounce to play!)",
        }
        self.setToolTip(tooltip_map.get(item_name, item_name))

    def _load_pixmap(self) -> None:
        path = os.path.join(SPRITES_DIR, "furniture", f"{self.item_name}.png")
        if os.path.exists(path):
            pm = QPixmap(path)
            self.pixmap = pm.scaled(
                self.item.size,
                self.item.size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )

    def sync_position(self) -> None:
        if not self.item.is_active:
            if self.isVisible():
                self.hide()
            return
        if not self.isVisible():
            self.show()
        if not self.item.is_dragging:
            self.move(int(self.item.x), int(self.item.y))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.item.is_dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.app_ctrl.show_context_menu(None, event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.item.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.move(new_pos)
            self.item.x = float(new_pos.x())
            self.item.y = float(new_pos.y())
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.item.is_dragging:
            self.item.is_dragging = False
            self.item.vx = 0.0
            self.item.vy = 0.0
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.item_name)
            event.accept()

    def paintEvent(self, event) -> None:
        if not self.pixmap:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.drawPixmap(0, 0, self.pixmap)
        p.end()


class PetWidget(QWidget):
    """Draggable interactive Pet Widget for Puppy or Kitten."""

    def __init__(
        self,
        pet: PetEntity,
        app_controller: "DesktopPetApp",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.pet = pet
        self.app_ctrl = app_controller
        self.drag_offset = QPoint()
        self.click_count = 0
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._reset_click_count)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self.resize(self.pet.pet_size, self.pet.pet_size)
        self.move(int(self.pet.x), int(self.pet.y))

        tooltip = "Puppy 🐶" if pet.name == "puppy" else "Kitten 🐱"
        self.setToolTip(f"{tooltip}\nDouble-click to snuggle! Right-click for options.")

    def _reset_click_count(self) -> None:
        self.click_count = 0

    def sync_position(self) -> None:
        if not self.pet.is_dragging:
            self.move(int(self.pet.x), int(self.pet.y))
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.pet.is_dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.app_ctrl.show_context_menu(self.pet.name, event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.pet.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.move(new_pos)
            self.pet.x = float(new_pos.x())
            self.pet.y = float(new_pos.y())
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.pet.is_dragging:
            self.pet.is_dragging = False
            self.pet.vx = 0.0
            self.pet.vy = 0.0
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_count = 0
            self.click_timer.stop()
            self.app_ctrl.trigger_pet_snuggle(self.pet.name)
            event.accept()

    def paintEvent(self, event) -> None:
        pm = self.app_ctrl.get_pet_pixmap(self.pet)
        if not pm:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.drawPixmap(0, 0, pm)
        p.end()


class SettingsButtonWidget(QWidget):
    """Floating draggable Settings Button for convenient one-click access to all actions and menus."""

    def __init__(
        self,
        app_controller: "DesktopPetApp",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.app_ctrl = app_controller
        self.drag_offset = QPoint()
        self.press_pos = QPoint()
        self.is_dragging = False
        self.is_hovered = False

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        if sys.platform == "darwin":
            flags |= Qt.WindowType.SubWindow
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        else:
            flags |= Qt.WindowType.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self.btn_size = 44
        self.resize(self.btn_size, self.btn_size)

        # Default position: near bottom right corner, above taskbar
        bounds = self.app_ctrl.bounds
        init_x = max(10, bounds.right - 64)
        init_y = max(10, bounds.bottom - 64)
        self.move(init_x, init_y)

        self.setToolTip("Pet Settings & Actions ⚙️\nClick to open menu, drag to reposition.")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event) -> None:
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event) -> None:
        self.is_hovered = False
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            self.press_pos = event.globalPosition().toPoint()
            self.drag_offset = self.press_pos - self.pos()
            self.is_dragging = False
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & (Qt.MouseButton.LeftButton | Qt.MouseButton.RightButton):
            curr_pos = event.globalPosition().toPoint()
            if (curr_pos - self.press_pos).manhattanLength() > 4:
                self.is_dragging = True
                self.move(curr_pos - self.drag_offset)
                event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            if not self.is_dragging:
                # User clicked without dragging -> trigger context menu at click location
                click_pos = event.globalPosition().toPoint()
                self.app_ctrl.show_context_menu(None, click_pos)
            self.is_dragging = False
            event.accept()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        rect = self.rect().adjusted(2, 2, -2, -2)

        # Background circle with subtle shadow/border
        if self.is_hovered:
            bg_color = QColor(40, 48, 64, 230)
            border_color = QColor(255, 215, 0, 220)  # Golden accent on hover
            gear_color = QColor(255, 255, 255)
        else:
            bg_color = QColor(28, 34, 48, 185)  # Elegant translucent slate
            border_color = QColor(220, 225, 235, 140)
            gear_color = QColor(235, 240, 245)

        p.setBrush(bg_color)
        p.setPen(border_color)
        p.drawEllipse(rect)

        font = QFont("Segoe UI Emoji", 18)
        if not font.exactMatch():
            font = QFont("Apple Color Emoji", 18)
        p.setFont(font)
        p.setPen(gear_color)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, "⚙️")
        p.end()


class DesktopPetApp:
    """Master controller managing both pets, furniture widgets, tray icon, and menus."""

    def __init__(self):
        self.bounds = get_screen_bounds()
        self.pet_size = 112
        self.engine = MultiPetEngine(self.bounds, pet_size=self.pet_size)

        # Sprite cache: dict[species][state][frame_idx][facing_right: bool] -> QPixmap
        self.sprite_cache: Dict[str, Dict[str, Dict[int, Dict[bool, QPixmap]]]] = {}
        self._load_all_sprites()

        # Widgets
        self.puppy_widget = PetWidget(self.engine.puppy, self)
        self.kitten_widget = PetWidget(self.engine.kitten, self)

        self.furniture_widgets: Dict[str, FurnitureWidget] = {}
        for fname, fitem in self.engine.furniture.items():
            fw = FurnitureWidget(fname, fitem, self)
            fw.double_clicked.connect(self._on_furniture_double_click)
            self.furniture_widgets[fname] = fw

        # Floating Settings Button
        self.settings_btn = SettingsButtonWidget(self)

        # System Tray
        self.tray_icon = QSystemTrayIcon()
        icon_path = os.path.join(BASE_DIR, "pet.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("Puppy & Cat Desktop Pets")
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

        # Show pet, furniture, and settings widgets
        for fw in self.furniture_widgets.values():
            if fw.item.is_active:
                fw.show()
        self.puppy_widget.show()
        self.kitten_widget.show()
        self.settings_btn.show()

        # Timers
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self._step_physics)
        self.physics_timer.start(30)

        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._step_frame)
        self.frame_timer.start(165)

        self.ai_timer = QTimer()
        self.ai_timer.timeout.connect(self._step_ai)
        self.ai_timer.start(7500)

        self.screen_timer = QTimer()
        self.screen_timer.timeout.connect(self._check_screen_bounds)
        self.screen_timer.start(2500)

    def _load_all_sprites(self) -> None:
        for pet_name in ("puppy", "kitten"):
            self.sprite_cache[pet_name] = {}
            for state in ("IDLE", "WALK", "PLAY", "SLEEP", "EAT", "SNUGGLE"):
                self.sprite_cache[pet_name][state] = {}
                state_prefix = state.lower()
                for idx in range(1, 5):
                    path = os.path.join(SPRITES_DIR, pet_name, f"{state_prefix}_{idx}.png")
                    if os.path.exists(path):
                        img = QImage(path)
                        # Scaled
                        img_scaled = img.scaled(
                            self.pet_size,
                            self.pet_size,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.FastTransformation,
                        )
                        # Mirrored for facing left (default sprite faces right)
                        img_flipped = img_scaled.mirrored(True, False)

                        self.sprite_cache[pet_name][state][idx - 1] = {
                            True: QPixmap.fromImage(img_scaled),
                            False: QPixmap.fromImage(img_flipped),
                        }

    def get_pet_pixmap(self, pet: PetEntity) -> Optional[QPixmap]:
        cache = self.sprite_cache.get(pet.name, {}).get(pet.state, {})
        frame_dict = cache.get(pet.frame_index)
        if not frame_dict:
            frame_dict = cache.get(0)
        if not frame_dict:
            return None
        facing_right = (pet.direction >= 0)
        return frame_dict.get(facing_right)

    def trigger_pet_snuggle(self, pet_name: str) -> None:
        pet = self.engine.puppy if pet_name == "puppy" else self.engine.kitten
        pet.trigger_snuggle()

        # Emit burst of heart particles
        heart_chars = ["💖", "💕", "✨", "💓", "🐾", "🌸"]
        base_x = int(pet.x + pet.pet_size * 0.5)
        base_y = int(pet.y + pet.pet_size * 0.3)
        for _ in range(7):
            char = random.choice(heart_chars)
            FloatingHeart(base_x + random.randint(-25, 25), base_y + random.randint(-15, 15), char=char)

    def trigger_both_snuggle(self) -> None:
        self.engine.both_snuggle()
        heart_chars = ["💖", "💕", "✨", "💓", "🐾", "🌸"]
        for pet in (self.engine.puppy, self.engine.kitten):
            base_x = int(pet.x + pet.pet_size * 0.5)
            base_y = int(pet.y + pet.pet_size * 0.3)
            for _ in range(6):
                char = random.choice(heart_chars)
                FloatingHeart(base_x + random.randint(-25, 25), base_y + random.randint(-15, 15), char=char)

    def trigger_both_eat(self) -> None:
        self.engine.call_both_to_eat()
        for b_name in ("puppy_bowl", "kitten_bowl"):
            self.furniture_widgets[b_name].show()
            item = self.engine.furniture[b_name]
            bx = int(item.x + item.size * 0.5)
            by = int(item.y + item.size * 0.2)
            for _ in range(4):
                char = random.choice(["🥣", "✨", "🍖", "🐟", "🐾"])
                FloatingHeart(bx + random.randint(-20, 20), by + random.randint(-10, 10), char=char)

    def trigger_both_bed(self) -> None:
        self.engine.bedtime_for_both()
        for b_name in ("puppy_bed", "kitten_bed"):
            self.furniture_widgets[b_name].show()
            item = self.engine.furniture[b_name]
            bx = int(item.x + item.size * 0.5)
            by = int(item.y + item.size * 0.2)
            for _ in range(4):
                char = random.choice(["💤", "✨", "🌙", "☁️"])
                FloatingHeart(bx + random.randint(-20, 20), by + random.randint(-10, 10), char=char)

    def trigger_both_wake(self) -> None:
        self.engine.wake_up_both()
        for pet in (self.engine.puppy, self.engine.kitten):
            base_x = int(pet.x + pet.pet_size * 0.5)
            base_y = int(pet.y + pet.pet_size * 0.3)
            for _ in range(5):
                char = random.choice(["☀️", "✨", "🐾", "🎉", "💖"])
                FloatingHeart(base_x + random.randint(-25, 25), base_y + random.randint(-15, 15), char=char)

    def _on_furniture_double_click(self, item_name: str) -> None:
        if item_name == "puppy_bed":
            self.engine.send_to_bed("puppy")
        elif item_name == "kitten_bed":
            self.engine.send_to_bed("kitten")
        elif item_name == "puppy_bowl":
            self.engine.send_to_bowl("puppy")
        elif item_name == "kitten_bowl":
            self.engine.send_to_bowl("kitten")
        elif item_name == "toy_ball":
            self.engine.bounce_toy_ball()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Context,
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            menu = self._build_menu()
            menu.exec(QCursor.pos())

    def _step_physics(self) -> None:
        # Cursor tracking
        if self.engine.follow_cursor:
            cursor_pos = QCursor.pos()
            self.engine.cursor_x = float(cursor_pos.x())
            self.engine.cursor_y = float(cursor_pos.y())

        self.engine.step_physics()

        # Sync widgets
        self.puppy_widget.sync_position()
        self.kitten_widget.sync_position()
        for fw in self.furniture_widgets.values():
            fw.sync_position()

    def _step_frame(self) -> None:
        self.engine.advance_frames()
        self.puppy_widget.update()
        self.kitten_widget.update()

    def _step_ai(self) -> None:
        self.engine.pick_random_states()

    def _check_screen_bounds(self) -> None:
        curr_bounds = get_screen_bounds()
        if (
            curr_bounds.left != self.bounds.left
            or curr_bounds.right != self.bounds.right
            or curr_bounds.bottom != self.bounds.bottom
        ):
            self.bounds = curr_bounds
            self.engine.update_bounds(curr_bounds)
            if hasattr(self, "settings_btn") and self.settings_btn:
                sb_x = min(max(self.bounds.left, self.settings_btn.x()), self.bounds.right - self.settings_btn.width())
                sb_y = min(max(self.bounds.top, self.settings_btn.y()), self.bounds.bottom - self.settings_btn.height())
                self.settings_btn.move(sb_x, sb_y)

    def set_pet_size(self, size: int) -> None:
        self.pet_size = size
        self.engine.pet_size = size
        self.engine.puppy.pet_size = size
        self.engine.kitten.pet_size = size
        self._load_all_sprites()
        self.puppy_widget.resize(size, size)
        self.kitten_widget.resize(size, size)
        self.engine.update_bounds(self.bounds)

    def toggle_furniture_visibility(self) -> None:
        all_active = all(self.engine.furniture[k].is_active for k in ("puppy_bed", "kitten_bed", "puppy_bowl", "kitten_bowl"))
        new_state = not all_active
        for k in ("puppy_bed", "kitten_bed", "puppy_bowl", "kitten_bowl"):
            self.engine.furniture[k].is_active = new_state
            if not new_state:
                self.furniture_widgets[k].hide()
            else:
                self.furniture_widgets[k].show()

    def _build_menu(self, context_pet: Optional[str] = None) -> QMenu:
        menu = QMenu()

        # ── Mutual Actions (Both Pets) ──
        both_header = menu.addAction("🐾 ── BOTH PETS OPTIONS ──")
        both_header.setEnabled(False)

        act_both_snuggle = menu.addAction("💖 Cuddle & Snuggle Both")
        act_both_snuggle.triggered.connect(lambda checked=False: self.trigger_both_snuggle())

        act_both_feed = menu.addAction("🥣 Call Both to Eat")
        act_both_feed.triggered.connect(lambda checked=False: self.trigger_both_eat())

        act_both_bed = menu.addAction("💤 Bedtime for Both")
        act_both_bed.triggered.connect(lambda checked=False: self.trigger_both_bed())

        act_both_wake = menu.addAction("☀️ Wake Up Both / Free Roam")
        act_both_wake.triggered.connect(lambda checked=False: self.trigger_both_wake())

        act_follow = menu.addAction("🐾 Follow Mouse Cursor (Toggle)")
        act_follow.setCheckable(True)
        act_follow.setChecked(self.engine.follow_cursor)
        act_follow.triggered.connect(lambda checked=False: self.engine.toggle_follow_cursor())

        ball_active = self.engine.furniture["toy_ball"].is_active
        if not ball_active:
            act_ball = menu.addAction("⚽ Spawn Play Toy Ball")
            act_ball.triggered.connect(lambda checked=False: self.engine.bounce_toy_ball())
        else:
            act_ball = menu.addAction("⚽ Bounce Toy Ball")
            act_ball.triggered.connect(lambda checked=False: self.engine.bounce_toy_ball())
            act_ball_hide = menu.addAction("📦 Put Away Toy Ball")
            act_ball_hide.triggered.connect(lambda checked=False: self.engine.put_away_toy_ball())

        menu.addSeparator()

        # ── Individual Pet Actions ──
        puppy_menu = menu.addMenu("🐶 Puppy Actions")
        act_p_bed = puppy_menu.addAction("Send Puppy to Bed 🛏️")
        act_p_bed.triggered.connect(lambda checked=False: self.engine.send_to_bed("puppy"))
        act_p_bowl = puppy_menu.addAction("Feed Puppy Bowl 🥣")
        act_p_bowl.triggered.connect(lambda checked=False: self.engine.send_to_bowl("puppy"))
        act_p_snuggle = puppy_menu.addAction("Puppy Cuddle & Snuggle 💖")
        act_p_snuggle.triggered.connect(lambda checked=False: self.trigger_pet_snuggle("puppy"))

        kitten_menu = menu.addMenu("🐱 Kitten Actions")
        act_k_bed = kitten_menu.addAction("Send Kitten to Bed 🛏️")
        act_k_bed.triggered.connect(lambda checked=False: self.engine.send_to_bed("kitten"))
        act_k_bowl = kitten_menu.addAction("Feed Kitten Bowl 🥣")
        act_k_bowl.triggered.connect(lambda checked=False: self.engine.send_to_bowl("kitten"))
        act_k_snuggle = kitten_menu.addAction("Kitten Cuddle & Snuggle 💖")
        act_k_snuggle.triggered.connect(lambda checked=False: self.trigger_pet_snuggle("kitten"))

        menu.addSeparator()

        # ── Settings & Controls ──
        settings_menu = menu.addMenu("⚙️ Settings")
        act_furn = settings_menu.addAction("Toggle Furniture Visible")
        act_furn.triggered.connect(lambda checked=False: self.toggle_furniture_visibility())

        size_menu = settings_menu.addMenu("📏 Pet Size")
        act_s = size_menu.addAction("Compact (80px)")
        act_s.triggered.connect(lambda checked=False: self.set_pet_size(80))
        act_m = size_menu.addAction("Normal (112px)")
        act_m.triggered.connect(lambda checked=False: self.set_pet_size(112))
        act_l = size_menu.addAction("Large (144px)")
        act_l.triggered.connect(lambda checked=False: self.set_pet_size(144))

        menu.addSeparator()

        act_quit = menu.addAction("❌ Exit Desktop Pets")
        act_quit.triggered.connect(lambda checked=False: self.quit_application())

        return menu

    def quit_application(self) -> None:
        if self.tray_icon:
            self.tray_icon.hide()
        if hasattr(self, "settings_btn") and self.settings_btn:
            self.settings_btn.hide()
        QApplication.quit()

    def show_context_menu(self, pet_name: Optional[str], pos: QPoint) -> None:
        menu = self._build_menu(pet_name)
        menu.exec(pos)


def main() -> None:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    icon_path = os.path.join(BASE_DIR, "pet.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    controller = DesktopPetApp()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
