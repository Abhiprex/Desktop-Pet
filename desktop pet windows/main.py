import os
import sys
import random
import math
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QTransform, QAction, QIcon, QCursor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QMenu,
    QSystemTrayIcon,
)

from pet_engine import PetEngine, ScreenBounds, VALID_STATES
from sprite_generator import ensure_sprites_exist

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITE_ROOT = os.path.join(BASE_DIR, "sprites")
STYLE_LABELS = {"cute": "Cute Griffin", "real": "Real Griffin"}
DEFAULT_STYLE = "cute"


def configure_floating_window(widget: QWidget) -> None:
    """Configure frameless, transparent, stays-on-top desktop overlay flags for macOS and Windows."""
    flags = (
        Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
    )
    if sys.platform == "darwin":
        # macOS AppKit/Cocoa: SubWindow keeps the desktop widget permanently afloat
        # and WA_MacAlwaysShowToolWindow prevents it from hiding when other apps are active
        flags |= Qt.WindowType.SubWindow
        widget.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        widget.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
    else:
        flags |= Qt.WindowType.Tool
    widget.setWindowFlags(flags)
    widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


class FloatingHeartParticle(QLabel):
    """A cheerful floating heart that flutters up and gently fades out when the pet is snuggled."""

    def __init__(self, x: float, y: float, size: int = 24, emoji: str = "💖"):
        super().__init__()
        configure_floating_window(self)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vx = random.uniform(-1.8, 1.8)
        self.vy = random.uniform(-3.5, -5.8)
        self.life = 0
        self.max_life = random.randint(30, 44)

        font = QFont("Segoe UI Emoji", size)
        if not font.exactMatch():
            font = QFont("Apple Color Emoji", size)
        self.setFont(font)
        self.setText(emoji)
        self.adjustSize()
        self.move(int(round(self.pos_x)), int(round(self.pos_y)))

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._step)
        self.anim_timer.start(28)
        self.show()

    def _step(self) -> None:
        self.life += 1
        if self.life >= self.max_life:
            try:
                self.anim_timer.stop()
                self.hide()
                self.deleteLater()
            except Exception:
                pass
            return
        self.pos_x += self.vx + math.sin(self.life * 0.28) * 0.7
        self.pos_y += self.vy
        self.vy *= 0.985
        self.move(int(round(self.pos_x)), int(round(self.pos_y)))
        remaining = self.max_life - self.life
        if remaining < 15:
            try:
                self.setWindowOpacity(max(0.0, remaining / 15.0))
            except Exception:
                pass


def get_app_icon() -> QIcon:
    """Return platform-appropriate icon (.icns on macOS, .ico on Windows, .png fallback)."""
    candidates = []
    if sys.platform == "darwin":
        candidates = ["pet.icns", os.path.join("sprites", "cute", "idle_1.png"), "pet.ico"]
    else:
        candidates = ["pet.ico", "pet.icns", os.path.join("sprites", "cute", "idle_1.png")]
    for c in candidates:
        p = os.path.join(BASE_DIR, c)
        if os.path.isfile(p):
            return QIcon(p)
    return QIcon()


class GriffinChooser(QDialog):
    """Startup window: pick which Griffin to see."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choose your Griffin")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowIcon(get_app_icon())
        self.choice = None

        outer = QVBoxLayout(self)
        title = QLabel("Which Griffin would you like to see?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; padding: 6px;")
        outer.addWidget(title)

        row = QHBoxLayout()
        for style, caption in (("cute", "Cute Griffin"), ("real", "Real Griffin")):
            ensure_sprites_exist(os.path.join(SPRITE_ROOT, style))
            pix = QPixmap(os.path.join(SPRITE_ROOT, style, "idle_1.png")).scaled(
                160, 160, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation
            )
            btn = QToolButton()
            btn.setText(caption)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(pix.size())
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setMinimumSize(190, 230)
            btn.setStyleSheet(
                "QToolButton { font-size: 14px; font-weight: bold; padding: 10px; border-radius: 8px; border: 2px solid #ccc; background: #ffffff; } "
                "QToolButton:hover { border-color: #f59e0b; background: #fffbeb; }"
            )
            btn.setProperty("style_name", style)
            btn.clicked.connect(lambda checked, s=style: self._pick(s))
            row.addWidget(btn)
        outer.addLayout(row)

    def _pick(self, style: str) -> None:
        self.choice = style
        self.accept()


class DraggableToyWidget(QWidget):
    """Separate transparent window for the interactive beach ball toy."""
    def __init__(self, engine: PetEngine, toy_pixmap: QPixmap):
        super().__init__()
        self.engine = engine
        configure_floating_window(self)
        self.setWindowIcon(get_app_icon())
        self.resize(self.engine.toy_size, self.engine.toy_size)

        self.label = QLabel(self)
        self.label.resize(self.engine.toy_size, self.engine.toy_size)
        self.label.setPixmap(
            toy_pixmap.scaled(
                self.engine.toy_size,
                self.engine.toy_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
        self.drag_offset = QPoint(0, 0)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.engine.toy_dragging = True
            self.engine.toy_vx = 0.0
            self.engine.toy_vy = 0.0
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event) -> None:
        if self.engine.toy_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            cx = self.engine.bounds.clamp_x(new_pos.x(), self.engine.toy_size)
            cy = self.engine.bounds.clamp_y(new_pos.y(), self.engine.toy_size)
            self.engine.toy_vx = (cx - self.engine.toy_x) * 0.5
            self.engine.toy_vy = (cy - self.engine.toy_y) * 0.4
            self.engine.toy_x = cx
            self.engine.toy_y = cy
            self.move(int(round(cx)), int(round(cy)))

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.engine.toy_dragging:
            self.engine.toy_dragging = False
            # If gently tapped/clicked, give a bouncy hop
            if abs(self.engine.toy_vx) < 1.0 and abs(self.engine.toy_vy) < 1.0:
                self.engine.toy_vy = -6.5
                self.engine.toy_vx = random.choice([-4.0, 4.0])
            else:
                self.engine.toy_vx = max(-15.0, min(15.0, self.engine.toy_vx))
                self.engine.toy_vy = max(-14.0, min(14.0, self.engine.toy_vy))
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.engine.bounce_toy(impulse_y=-9.5)

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        bounce_action = QAction("Bounce Ball ⚽", self)
        bounce_action.triggered.connect(self.engine.bounce_toy)
        menu.addAction(bounce_action)
        put_away_action = QAction("Put Away Ball", self)
        put_away_action.triggered.connect(self.put_away)
        menu.addAction(put_away_action)
        menu.exec(event.globalPos())

    def put_away(self) -> None:
        self.engine.despawn_toy()
        self.hide()


class DraggableBedWidget(QWidget):
    """Separate transparent window for the permanent cozy pet bed."""
    def __init__(self, engine: PetEngine, bed_pixmap: QPixmap, parent_pet=None):
        super().__init__()
        self.engine = engine
        self.parent_pet = parent_pet
        configure_floating_window(self)
        self.setWindowIcon(get_app_icon())
        self.resize(self.engine.bed_size, self.engine.bed_size)

        self.label = QLabel(self)
        self.label.resize(self.engine.bed_size, self.engine.bed_size)
        self.set_pixmap(bed_pixmap)
        self.drag_offset = QPoint(0, 0)
        self.setToolTip("Cozy Pet Bed 🛏️ (Drag anywhere, double-click to nap)")

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self.label.setPixmap(
            pixmap.scaled(
                self.engine.bed_size,
                self.engine.bed_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.engine.bed_dragging = True
            self.engine.bed_vx = 0.0
            self.engine.bed_vy = 0.0
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.engine.on_bed_moved()
        elif event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)
            nap_action = QAction("Nap in Bed 💤", self)
            if self.parent_pet:
                nap_action.triggered.connect(self.parent_pet.go_to_bed_and_nap)
            menu.addAction(nap_action)
            hide_action = QAction("Put Away Bed", self)
            if self.parent_pet:
                hide_action.triggered.connect(lambda: self.parent_pet.toggle_bed(False))
            else:
                hide_action.triggered.connect(self.hide)
            menu.addAction(hide_action)
            menu.exec(event.globalPosition().toPoint())
            if self.parent_pet:
                self.parent_pet.raise_()

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.parent_pet:
            self.parent_pet.go_to_bed_and_nap()
            self.parent_pet.raise_()

    def mouseMoveEvent(self, event) -> None:
        if self.engine.bed_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            cx = self.engine.bounds.clamp_x(new_pos.x(), self.engine.bed_size)
            cy = self.engine.bounds.clamp_y(new_pos.y(), self.engine.bed_size)
            self.engine.bed_vx = (cx - self.engine.bed_x) * 0.5
            self.engine.bed_vy = (cy - self.engine.bed_y) * 0.4
            self.engine.bed_x = float(cx)
            self.engine.bed_y = float(cy)
            self.move(int(round(cx)), int(round(cy)))
            self.engine.on_bed_moved()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.engine.bed_dragging:
            self.engine.bed_dragging = False
            self.engine.bed_vx = max(-10.0, min(10.0, self.engine.bed_vx))
            self.engine.bed_vy = max(-8.0, min(8.0, self.engine.bed_vy))
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            if self.parent_pet:
                self.parent_pet.raise_()


class DraggableFoodBowlWidget(QWidget):
    """Separate transparent window for the permanent snack food bowl."""
    def __init__(self, engine: PetEngine, bowl_pixmap: QPixmap, parent_pet=None):
        super().__init__()
        self.engine = engine
        self.parent_pet = parent_pet
        configure_floating_window(self)
        self.setWindowIcon(get_app_icon())
        self.resize(self.engine.bowl_size, self.engine.bowl_size)

        self.label = QLabel(self)
        self.label.resize(self.engine.bowl_size, self.engine.bowl_size)
        self.set_pixmap(bowl_pixmap)
        self.drag_offset = QPoint(0, 0)
        self.setToolTip("Snack Food Bowl 🥣 (Drag anywhere, double-click to feed)")

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self.label.setPixmap(
            pixmap.scaled(
                self.engine.bowl_size,
                self.engine.bowl_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.engine.bowl_dragging = True
            self.engine.bowl_vx = 0.0
            self.engine.bowl_vy = 0.0
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.engine.on_bowl_moved()
        elif event.button() == Qt.MouseButton.RightButton:
            menu = QMenu(self)
            eat_action = QAction("Eat from Bowl 🌟", self)
            if self.parent_pet:
                eat_action.triggered.connect(self.parent_pet.go_to_bowl_and_eat)
            menu.addAction(eat_action)
            hide_action = QAction("Put Away Food Bowl", self)
            if self.parent_pet:
                hide_action.triggered.connect(lambda: self.parent_pet.toggle_food_bowl(False))
            else:
                hide_action.triggered.connect(self.hide)
            menu.addAction(hide_action)
            menu.exec(event.globalPosition().toPoint())
            if self.parent_pet:
                self.parent_pet.raise_()

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.parent_pet:
            self.parent_pet.go_to_bowl_and_eat()
            self.parent_pet.raise_()

    def mouseMoveEvent(self, event) -> None:
        if self.engine.bowl_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            cx = self.engine.bounds.clamp_x(new_pos.x(), self.engine.bowl_size)
            cy = self.engine.bounds.clamp_y(new_pos.y(), self.engine.bowl_size)
            self.engine.bowl_vx = (cx - self.engine.bowl_x) * 0.5
            self.engine.bowl_vy = (cy - self.engine.bowl_y) * 0.4
            self.engine.bowl_x = float(cx)
            self.engine.bowl_y = float(cy)
            self.move(int(round(cx)), int(round(cy)))
            self.engine.on_bowl_moved()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.engine.bowl_dragging:
            self.engine.bowl_dragging = False
            self.engine.bowl_vx = max(-10.0, min(10.0, self.engine.bowl_vx))
            self.engine.bowl_vy = max(-8.0, min(8.0, self.engine.bowl_vy))
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            if self.parent_pet:
                self.parent_pet.raise_()


class CozyDesktopPet(QWidget):
    def __init__(self, pet_size: int = 112, style: str = DEFAULT_STYLE):
        super().__init__()
        self.style = style if style in STYLE_LABELS else DEFAULT_STYLE
        self.sprite_dir = os.path.join(SPRITE_ROOT, self.style)
        ensure_sprites_exist(self.sprite_dir)

        configure_floating_window(self)
        self.setWindowIcon(get_app_icon())

        self.pet_size = pet_size
        self.label = QLabel(self)
        self.resize(self.pet_size, self.pet_size)
        self.label.resize(self.pet_size, self.pet_size)

        screen_bounds = self._query_screen_bounds()
        self.engine = PetEngine(bounds=screen_bounds, pet_size=self.pet_size)

        screen = QApplication.primaryScreen()
        if screen:
            screen.availableGeometryChanged.connect(self._on_screen_geometry_changed)

        self.sprites_right = {}
        self.sprites_left = {}
        self._load_all_sprites()

        self.toy_widget = DraggableToyWidget(self.engine, QPixmap(os.path.join(self.sprite_dir, "toy.png")))
        self.bed_widget = DraggableBedWidget(
            self.engine,
            QPixmap(os.path.join(self.sprite_dir, "bed.png")),
            parent_pet=self,
        )
        self.bowl_widget = DraggableFoodBowlWidget(
            self.engine,
            QPixmap(os.path.join(self.sprite_dir, "food_bowl.png")),
            parent_pet=self,
        )

        self.drag_offset = QPoint(0, 0)
        self.move(int(self.engine.x), int(self.engine.y))

        self.click_count = 0
        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._reset_click_count)
        self.active_hearts = []

        self.tray_icon = None
        self._setup_system_tray()

        self.physics_timer = QTimer(self)
        self.physics_timer.timeout.connect(self.on_physics_tick)
        self.physics_timer.start(28)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.on_animation_tick)
        self.anim_timer.start(180)

        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self.on_state_decision)
        self.state_timer.start(6000)

        self.render_current_frame()

    def _query_screen_bounds(self) -> ScreenBounds:
        screen = QApplication.primaryScreen()
        if screen is None:
            return ScreenBounds(0, 0, 1920, 1040)
        geom = screen.availableGeometry()
        return ScreenBounds(
            left=geom.left(),
            top=geom.top(),
            right=geom.left() + geom.width(),
            bottom=geom.top() + geom.height(),
        )

    def _on_screen_geometry_changed(self, geom) -> None:
        """Handle macOS Dock resize / position change or external display connect/disconnect."""
        self.engine.update_bounds(self._query_screen_bounds())

    def _load_all_sprites(self) -> None:
        mirror_transform = QTransform().scale(-1, 1)
        for state in VALID_STATES:
            right_frames = []
            left_frames = []
            for idx in range(1, 5):
                filename = f"{state.lower()}_{idx}.png"
                path = os.path.join(self.sprite_dir, filename)
                pixmap = QPixmap(path)
                if pixmap.isNull():
                    pixmap = QPixmap(self.pet_size, self.pet_size)
                    pixmap.fill(Qt.GlobalColor.transparent)
                else:
                    pixmap = pixmap.scaled(
                        self.pet_size,
                        self.pet_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation,
                    )
                right_frames.append(pixmap)
                left_frames.append(pixmap.transformed(mirror_transform))

            self.sprites_right[state] = right_frames
            self.sprites_left[state] = left_frames

        # Also load contextual action sprites (eating at bowl, napping inside bed)
        for extra in ("eat_bowl", "sleep_bed"):
            right_frames = []
            left_frames = []
            for idx in range(1, 5):
                filename = f"{extra}_{idx}.png"
                path = os.path.join(self.sprite_dir, filename)
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        self.pet_size,
                        self.pet_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation,
                    )
                    right_frames.append(pixmap)
                    left_frames.append(pixmap.transformed(mirror_transform))
            if right_frames:
                self.sprites_right[extra] = right_frames
                self.sprites_left[extra] = left_frames

        self.engine.frame_counts = {s: len(self.sprites_right[s]) for s in VALID_STATES}

    def _setup_system_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon_path = os.path.join(self.sprite_dir, "idle_1.png")
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        self.tray_icon.setToolTip(f"{STYLE_LABELS[self.style]} Desktop Pet")
        self.tray_icon.setContextMenu(self._build_context_menu())
        self.tray_icon.show()

    def on_physics_tick(self) -> None:
        if self.engine.follow_cursor:
            cpos = QCursor.pos()
            self.engine.cursor_x = float(cpos.x())
            self.engine.cursor_y = float(cpos.y())
        self.engine.step_physics()
        target_x, target_y = int(round(self.engine.x)), int(round(self.engine.y))
        if self.x() != target_x or self.y() != target_y:
            self.move(target_x, target_y)

        if self.engine.toy_active:
            tx, ty = int(round(self.engine.toy_x)), int(round(self.engine.toy_y))
            if self.toy_widget.x() != tx or self.toy_widget.y() != ty:
                self.toy_widget.move(tx, ty)
            if not self.toy_widget.isVisible():
                self.toy_widget.show()
        elif self.toy_widget.isVisible():
            self.toy_widget.hide()

        if self.engine.bed_active:
            bx, by = int(round(self.engine.bed_x)), int(round(self.engine.bed_y))
            if self.bed_widget.x() != bx or self.bed_widget.y() != by:
                self.bed_widget.move(bx, by)
            if not self.bed_widget.isVisible():
                self.bed_widget.show()
                self.raise_()
            if not self.engine.bed_dragging:
                self.raise_()
        elif self.bed_widget.isVisible():
            self.bed_widget.hide()

        if self.engine.bowl_active:
            bx, by = int(round(self.engine.bowl_x)), int(round(self.engine.bowl_y))
            if self.bowl_widget.x() != bx or self.bowl_widget.y() != by:
                self.bowl_widget.move(bx, by)
            if not self.bowl_widget.isVisible():
                self.bowl_widget.show()
                self.raise_()
            if not self.engine.bowl_dragging:
                self.raise_()
        elif self.bowl_widget.isVisible():
            self.bowl_widget.hide()

    def on_animation_tick(self) -> None:
        if self.engine.flying_mode and self.engine.state != "JUMP":
            self.engine.state = "JUMP"
        self.engine.advance_frame()
        self.render_current_frame()

    def on_state_decision(self) -> None:
        self.engine.pick_next_state()
        intervals = {"WALK": 150, "PLAY": 145, "IDLE": 240, "SLEEP": 380, "EAT": 220, "JUMP": 115}
        self.anim_timer.setInterval(intervals.get(self.engine.state, 200))
        self.state_timer.setInterval(random.randint(4500, 9000))
        self.render_current_frame()

    def render_current_frame(self) -> None:
        state = self.engine.state
        idx = self.engine.frame_index

        if state == "EAT" and getattr(self.engine, "is_eating_at_bowl", False) and "eat_bowl" in self.sprites_right:
            effective_state = "eat_bowl"
        elif state == "SLEEP" and getattr(self.engine, "is_sleeping_in_bed", False) and "sleep_bed" in self.sprites_right:
            effective_state = "sleep_bed"
        else:
            effective_state = state

        if self.engine.direction == -1 and effective_state in ("WALK", "IDLE", "PLAY", "EAT", "JUMP", "eat_bowl", "sleep_bed"):
            frames = self.sprites_left[effective_state]
        else:
            frames = self.sprites_right[effective_state]
        self.label.setPixmap(frames[idx % len(frames)])

    def force_state(self, new_state: str) -> None:
        if new_state in ("WALK", "SLEEP", "IDLE", "EAT", "PLAY"):
            # Explicit ground action: land on the taskbar/floor and disable continuous flying mode
            self.engine.flying_mode = False
            self.engine.y = self.engine.floor_y
            self.engine.vy = 0.0
        if new_state == "JUMP":
            self.engine.trigger_jump()
        elif new_state == "EAT":
            self.engine.feed_snack()
        else:
            self.engine.set_state(new_state)
        intervals = {"WALK": 150, "PLAY": 145, "IDLE": 240, "SLEEP": 380, "EAT": 220, "JUMP": 115}
        self.anim_timer.setInterval(intervals.get(new_state, 200))
        self.state_timer.start(8000)
        self.render_current_frame()

    def toggle_flying_mode(self) -> None:
        self.engine.toggle_flying()
        intervals = {"WALK": 150, "PLAY": 145, "IDLE": 240, "SLEEP": 380, "EAT": 220, "JUMP": 115}
        self.anim_timer.setInterval(intervals.get(self.engine.state, 115))
        self.render_current_frame()

    def toggle_toy_ball(self) -> None:
        if self.engine.toy_active:
            self.engine.despawn_toy()
            self.toy_widget.hide()
        else:
            self.engine.spawn_toy()
            self.toy_widget.move(int(round(self.engine.toy_x)), int(round(self.engine.toy_y)))
            self.toy_widget.show()

    def bounce_toy_ball(self) -> None:
        self.engine.bounce_toy()
        if not self.toy_widget.isVisible():
            self.toy_widget.move(int(round(self.engine.toy_x)), int(round(self.engine.toy_y)))
            self.toy_widget.show()

    def toggle_bed(self, enable: Optional[bool] = None) -> bool:
        """Toggle or set permanent bed visibility on the screen."""
        active = self.engine.toggle_bed(enable)
        if active:
            bx, by = int(round(self.engine.bed_x)), int(round(self.engine.bed_y))
            self.bed_widget.move(bx, by)
            self.bed_widget.show()
            self.raise_()
        else:
            self.bed_widget.hide()
        return active

    def toggle_food_bowl(self, enable: Optional[bool] = None) -> bool:
        """Toggle or set permanent food bowl visibility on the screen."""
        active = self.engine.toggle_bowl(enable)
        if active:
            bx, by = int(round(self.engine.bowl_x)), int(round(self.engine.bowl_y))
            self.bowl_widget.move(bx, by)
            self.bowl_widget.show()
            self.raise_()
        else:
            self.bowl_widget.hide()
        return active

    def go_to_bed_and_nap(self) -> None:
        """Make the pet walk over to the bed and sleep comfortably in it."""
        if not self.engine.bed_active:
            self.toggle_bed(True)
        self.engine.go_to_bed()
        self.raise_()
        intervals = {"WALK": 150, "PLAY": 145, "IDLE": 240, "SLEEP": 380, "EAT": 220, "JUMP": 115}
        self.anim_timer.setInterval(intervals.get(self.engine.state, 150))
        self.state_timer.start(14000)
        self.render_current_frame()

    def go_to_bowl_and_eat(self) -> None:
        """Make the pet walk over to the food bowl and eat its snacks."""
        if not self.engine.bowl_active:
            self.toggle_food_bowl(True)
        self.engine.go_to_bowl()
        self.raise_()
        intervals = {"WALK": 150, "PLAY": 145, "IDLE": 240, "SLEEP": 380, "EAT": 220, "JUMP": 115}
        self.anim_timer.setInterval(intervals.get(self.engine.state, 150))
        self.state_timer.start(12000)
        self.render_current_frame()

    def _reset_click_count(self) -> None:
        self.click_count = 0

    def trigger_snuggle(self, *args) -> None:
        """Pet gets all snuggly, hearts fly, and cuddly animation plays!"""
        self.engine.trigger_snuggle()
        self.anim_timer.setInterval(120)
        self.state_timer.start(4500)
        self.render_current_frame()
        self.spawn_flying_hearts(random.randint(6, 9))

    def spawn_flying_hearts(self, count: int = 7) -> None:
        emojis = ["💖", "💕", "✨", "💓", "💗", "❤️"]
        valid_hearts = []
        for h in self.active_hearts:
            try:
                if h.isVisible():
                    valid_hearts.append(h)
            except Exception:
                pass
        self.active_hearts = valid_hearts

        for _ in range(count):
            ox = random.uniform(10, max(20, self.pet_size - 30))
            oy = random.uniform(10, max(20, self.pet_size * 0.6))
            try:
                h = FloatingHeartParticle(
                    self.x() + ox,
                    self.y() + oy,
                    size=random.randint(18, 26),
                    emoji=random.choice(emojis),
                )
                self.active_hearts.append(h)
            except Exception:
                pass

    def toggle_follow_cursor(self, enable: Optional[bool] = None, *args) -> bool:
        """Toggle cursor following mode on/off."""
        active = self.engine.toggle_follow_cursor(enable)
        if active:
            self.anim_timer.setInterval(140)
        else:
            self.anim_timer.setInterval(200)
        self.render_current_frame()
        return active

    def change_style(self, new_style: str) -> None:
        """Switch between the Cute and Real griffin without restarting."""
        if new_style not in STYLE_LABELS or new_style == self.style:
            return
        self.style = new_style
        self.sprite_dir = os.path.join(SPRITE_ROOT, new_style)
        ensure_sprites_exist(self.sprite_dir)
        self._load_all_sprites()
        self.toy_widget.label.setPixmap(
            QPixmap(os.path.join(self.sprite_dir, "toy.png")).scaled(
                self.engine.toy_size,
                self.engine.toy_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )
        self.bed_widget.set_pixmap(QPixmap(os.path.join(self.sprite_dir, "bed.png")))
        self.bowl_widget.set_pixmap(QPixmap(os.path.join(self.sprite_dir, "food_bowl.png")))
        if self.tray_icon is not None:
            self.tray_icon.setIcon(QIcon(os.path.join(self.sprite_dir, "idle_1.png")))
            self.tray_icon.setToolTip(f"{STYLE_LABELS[self.style]} Desktop Pet")
        self.render_current_frame()

    def change_size(self, new_size: int) -> None:
        self.pet_size = new_size
        self.resize(self.pet_size, self.pet_size)
        self.label.resize(self.pet_size, self.pet_size)
        self.engine.pet_size = self.pet_size
        self.engine.update_bounds(self._query_screen_bounds())
        self._load_all_sprites()
        self.move(int(round(self.engine.x)), int(round(self.engine.y)))
        self.render_current_frame()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_count += 1
            self.click_timer.start(450)
            if self.click_count >= 2:
                self.trigger_snuggle()
                self.click_count = 0
            self.engine.start_drag()
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            self.render_current_frame()
        elif event.button() == Qt.MouseButton.RightButton:
            menu = self._build_context_menu()
            menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event) -> None:
        if self.engine.is_dragging:
            new_pos = event.globalPosition().toPoint() - self.drag_offset
            self.engine.drag_to(new_pos.x(), new_pos.y())
            self.move(int(round(self.engine.x)), int(round(self.engine.y)))

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.engine.is_dragging:
            self.engine.end_drag()
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # Multi-click or double-click: pet gets snuggly and hearts fly!
            if self.click_count < 2:
                self.trigger_snuggle()
            self.click_count = 0

    def closeEvent(self, event) -> None:
        for h in getattr(self, "active_hearts", []):
            try:
                h.hide()
                h.deleteLater()
            except Exception:
                pass
        self.active_hearts = []
        if hasattr(self, "toy_widget"):
            self.toy_widget.close()
        if hasattr(self, "bed_widget"):
            self.bed_widget.close()
        if hasattr(self, "bowl_widget"):
            self.bowl_widget.close()
        if self.tray_icon is not None:
            self.tray_icon.hide()
        super().closeEvent(event)

    def _build_context_menu(self) -> QMenu:
        menu = QMenu(self)

        # Interactive Toy Ball section
        if self.engine.toy_active:
            bounce_action = QAction("Bounce Toy Ball ⚽", self)
            bounce_action.triggered.connect(lambda checked: self.bounce_toy_ball())
            menu.addAction(bounce_action)

            toy_action = QAction("Put Away Toy Ball", self)
            toy_action.triggered.connect(lambda checked: self.toggle_toy_ball())
            menu.addAction(toy_action)
        else:
            toy_action = QAction("Spawn Toy Ball ⚽", self)
            toy_action.triggered.connect(lambda checked: self.toggle_toy_ball())
            menu.addAction(toy_action)

        menu.addSeparator()
        # Permanent Desktop Items (Bed & Food Bowl)
        bed_action = QAction("Cozy Pet Bed 🛏️ (Keep on Screen)", self)
        bed_action.setCheckable(True)
        bed_action.setChecked(self.engine.bed_active)
        bed_action.triggered.connect(lambda: self.toggle_bed())
        menu.addAction(bed_action)

        bowl_action = QAction("Snack Food Bowl 🥣 (Keep on Screen)", self)
        bowl_action.setCheckable(True)
        bowl_action.setChecked(self.engine.bowl_active)
        bowl_action.triggered.connect(lambda: self.toggle_food_bowl())
        menu.addAction(bowl_action)

        menu.addSeparator()
        fly_action = QAction("Fly Around Screen 🦅 (Continuous Flying Mode)", self)
        fly_action.setCheckable(True)
        fly_action.setChecked(self.engine.flying_mode)
        fly_action.triggered.connect(lambda checked: self.toggle_flying_mode())
        menu.addAction(fly_action)

        follow_action = QAction("Follow Mouse Cursor 🐾", self)
        follow_action.setCheckable(True)
        follow_action.setChecked(self.engine.follow_cursor)
        follow_action.triggered.connect(lambda checked: self.toggle_follow_cursor(checked))
        menu.addAction(follow_action)

        snuggle_action = QAction("Snuggle & Cuddle 💖", self)
        snuggle_action.triggered.connect(lambda checked: self.trigger_snuggle())
        menu.addAction(snuggle_action)

        menu.addSeparator()
        for label_text, state_name in [
            ("Walk on Ground 🐾", "WALK"),
            ("Feed Star Cookie 🌟", "EAT"),
            ("Cloud Pillow Nap 💤", "SLEEP"),
        ]:
            action = QAction(label_text, self)
            if state_name == "SLEEP":
                action.triggered.connect(lambda checked: self.go_to_bed_and_nap() if self.engine.bed_active else self.force_state("SLEEP"))
            elif state_name == "EAT":
                action.triggered.connect(lambda checked: self.go_to_bowl_and_eat() if self.engine.bowl_active else self.force_state("EAT"))
            else:
                action.triggered.connect(lambda checked, s=state_name: self.force_state(s))
            menu.addAction(action)

        menu.addSeparator()
        style_menu = menu.addMenu("Switch Griffin")
        for style_key, style_label in STYLE_LABELS.items():
            style_action = QAction(style_label, self)
            style_action.setCheckable(True)
            style_action.setChecked(style_key == self.style)
            style_action.triggered.connect(lambda checked, k=style_key: self.change_style(k))
            style_menu.addAction(style_action)

        size_menu = menu.addMenu("Pet Size")
        for size_label, px_size in [("Small (80px)", 80), ("Medium (112px)", 112), ("Large (144px)", 144)]:
            size_action = QAction(size_label, self)
            size_action.triggered.connect(lambda checked, sz=px_size: self.change_size(sz))
            size_menu.addAction(size_action)

        menu.addSeparator()
        quit_action = QAction("Exit Pet", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        return menu


def run(style=None, size=112, bed=False, bowl=False):
    # Ensure Windows taskbar groups and shows the custom icon properly (Windows only)
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cozy.desktop.pet.griffin.v4")
        except Exception:
            pass

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setQuitOnLastWindowClosed(False)

    if sys.platform == "darwin":
        # macOS AppKit configuration: preserve running state and app metadata
        app.setApplicationName("Desktop Pet Griffin")
        app.setApplicationDisplayName("Desktop Pet Griffin")

    app.setWindowIcon(get_app_icon())

    chosen_style = style
    if chosen_style is None:
        chooser = GriffinChooser()
        if chooser.exec() != QDialog.DialogCode.Accepted or chooser.choice is None:
            return 0
        chosen_style = chooser.choice

    pet = CozyDesktopPet(pet_size=size, style=chosen_style)
    if bed:
        pet.toggle_bed(True)
    if bowl:
        pet.toggle_food_bowl(True)
    pet.show()
    return app.exec()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cozy Desktop Pet - Griffin Edition")
    parser.add_argument(
        "--style",
        choices=["cute", "real"],
        default=None,
        help="Start with a specific Griffin style without prompting",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=112,
        help="Pet size in pixels (default: 112)",
    )
    parser.add_argument(
        "--bed",
        action="store_true",
        help="Start with cozy pet bed permanently on desktop",
    )
    parser.add_argument(
        "--bowl",
        action="store_true",
        help="Start with snack food bowl permanently on desktop",
    )
    args, unknown = parser.parse_known_args()
    sys.exit(run(style=args.style, size=args.size, bed=args.bed, bowl=args.bowl))
