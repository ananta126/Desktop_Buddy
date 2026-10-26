"""
Desktop Buddy — break-reminder prototype.

Run:
    py -m pip install -r requirements.txt
    py main.py

This prototype uses original Qt-drawn placeholder characters. Replace them
only with assets you are allowed to redistribute.
"""
from __future__ import annotations

import math
import random
import sys
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QRadialGradient
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QCheckBox, QGroupBox, QSystemTrayIcon, QMenu, QStyle
)

try:
    import winsound  # Windows only
except ImportError:
    winsound = None


APP_NAME = "Desktop Buddy"


def play_effect(enabled: bool, kind: str = "alert") -> None:
    """Play a short built-in sound cue without external audio files."""
    if not enabled:
        return
    try:
        if winsound:
            if kind == "start":
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                winsound.Beep(880, 100)
                winsound.Beep(1175, 130)
            elif kind == "end":
                winsound.Beep(740, 100)
                winsound.Beep(988, 130)
            else:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            QApplication.beep()
    except Exception:
        QApplication.beep()


class CloneOverlay(QWidget):
    """A temporary full-screen animated overlay with safe dismissal."""
    def __init__(self, break_minutes: int, sound_enabled: bool, on_finished):
        super().__init__()
        self.remaining = max(1, break_minutes * 60)
        self.sound_enabled = sound_enabled
        self.on_finished = on_finished
        self.phase = 0.0
        self._button_rects: tuple[QRectF, QRectF] | None = None
        self.clones = []

        screen = QApplication.primaryScreen()
        geometry = screen.geometry() if screen else QRectF(0, 0, 1280, 720)
        width, height = geometry.width(), geometry.height()
        count = max(18, min(44, int(width * height / 42000)))
        for _ in range(count):
            self.clones.append({
                "x": random.uniform(.03, .97),
                "y": random.uniform(.07, .92),
                "scale": random.uniform(.65, 1.18),
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(.7, 1.5),
                "tilt": random.uniform(-10, 10),
                "color": random.choice(["#ff8c22", "#ffad42", "#ffd18b"]),
            })

        self.setWindowTitle("Shadow Clone Break")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setGeometry(geometry)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(40)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self._tick)
        self.countdown_timer.start(1000)
        play_effect(self.sound_enabled, "start")

    def _animate(self):
        self.phase += .075
        self.update()

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.close()
            self.on_finished("complete")
        else:
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
        else:
            super().keyPressEvent(event)

    def dismiss(self):
        self.close()
        self.on_finished("dismissed")

    def snooze(self):
        self.close()
        self.on_finished("snoozed")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        painter.fillRect(self.rect(), QColor("#171021"))
        glow = QRadialGradient(QPointF(w * .5, h * .45), max(w, h) * .72)
        glow.setColorAt(0, QColor(255, 112, 26, 130))
        glow.setColorAt(.58, QColor(119, 44, 103, 95))
        glow.setColorAt(1, QColor(14, 10, 28, 245))
        painter.fillRect(self.rect(), QBrush(glow))

        # Energy rings
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(4):
            radius = 75 + i * 62 + (self.phase * 24) % 62
            painter.setPen(QPen(QColor(93, 190, 255, max(20, 100 - i * 18)), 3))
            painter.drawEllipse(QPointF(w * .5, h * .48), radius, radius)

        # Stylised placeholder clones, drawn with Qt (no external assets).
        for clone in self.clones:
            bob = math.sin(self.phase * clone["speed"] + clone["phase"]) * 12
            painter.save()
            painter.translate(clone["x"] * w, clone["y"] * h + bob)
            painter.rotate(clone["tilt"] * math.sin(self.phase + clone["phase"]))
            painter.scale(clone["scale"], clone["scale"])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, 85))
            painter.drawEllipse(QRectF(-28, 24, 56, 14))
            painter.setBrush(QColor(clone["color"]))
            painter.drawRoundedRect(QRectF(-22, -2, 44, 45), 12, 12)
            painter.setBrush(QColor("#ffd4a5"))
            painter.drawEllipse(QRectF(-21, -38, 42, 42))
            painter.setBrush(QColor("#f4a623"))
            painter.drawPolygon([
                QPointF(-20, -25), QPointF(-27, -43), QPointF(-13, -37),
                QPointF(-5, -51), QPointF(2, -38), QPointF(15, -47),
                QPointF(21, -29), QPointF(15, -35), QPointF(-15, -33)
            ])
            painter.setBrush(QColor("#343541"))
            painter.drawRoundedRect(QRectF(-20, -29, 40, 8), 3, 3)
            painter.setPen(QPen(QColor("#cbd5e1"), 1.5))
            painter.drawLine(QPointF(-8, -25), QPointF(8, -25))
            painter.setPen(QPen(QColor("#24212a"), 2))
            painter.drawLine(QPointF(-10, -17), QPointF(-5, -17))
            painter.drawLine(QPointF(5, -17), QPointF(10, -17))
            painter.drawArc(QRectF(-7, -13, 14, 9), 200 * 16, 140 * 16)
            painter.setPen(QPen(QColor(clone["color"]), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            wave = math.sin(self.phase * 2 + clone["phase"]) * 8
            painter.drawLine(QPointF(-18, 8), QPointF(-32, 1 + wave))
            painter.drawLine(QPointF(18, 8), QPointF(32, 1 - wave))
            painter.restore()

        # Main message panel
        panel_w, panel_h = min(690, w - 36), 230
        px, py = (w - panel_w) / 2, max(18, h * .5 - panel_h / 2)
        painter.setPen(QPen(QColor(255, 255, 255, 75), 1))
        painter.setBrush(QColor(15, 12, 28, 225))
        painter.drawRoundedRect(QRectF(px, py, panel_w, panel_h), 24, 24)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 23, QFont.Weight.Bold))
        painter.drawText(QRectF(px + 20, py + 16, panel_w - 40, 42),
                         Qt.AlignmentFlag.AlignCenter, "SHADOW CLONE JUTSU!")
        painter.setFont(QFont("Segoe UI", 13))
        painter.setPen(QColor("#ffe2bd"))
        painter.drawText(QRectF(px + 20, py + 59, panel_w - 40, 30),
                         Qt.AlignmentFlag.AlignCenter, "Break time, ninja. Stretch, hydrate, and rest your eyes.")
        mins, secs = divmod(max(0, self.remaining), 60)
        painter.setPen(QColor("#8ed8ff"))
        painter.setFont(QFont("Consolas", 29, QFont.Weight.Bold))
        painter.drawText(QRectF(px + 20, py + 90, panel_w - 40, 48),
                         Qt.AlignmentFlag.AlignCenter, f"{mins:02d}:{secs:02d}")
        painter.setPen(QColor("#e7e1f3"))
        painter.setFont(QFont("Segoe UI", 10))
        painter.drawText(QRectF(px + 20, py + 139, panel_w - 40, 22),
                         Qt.AlignmentFlag.AlignCenter, "Press Esc to dismiss • Snooze adds five minutes")

        bw, bh, gap = 145, 38, 14
        total = bw * 2 + gap
        bx, by = (w - total) / 2, py + 178
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#ff922e"))
        painter.drawRoundedRect(QRectF(bx, by, bw, bh), 10, 10)
        painter.setBrush(QColor("#3e3958"))
        painter.drawRoundedRect(QRectF(bx + bw + gap, by, bw, bh), 10, 10)
        painter.setPen(QColor("#201225"))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(bx, by, bw, bh), Qt.AlignmentFlag.AlignCenter, "Dismiss")
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(bx + bw + gap, by, bw, bh), Qt.AlignmentFlag.AlignCenter, "Snooze +5 min")
        self._button_rects = (
            QRectF(bx, by, bw, bh),
            QRectF(bx + bw + gap, by, bw, bh),
        )

    def mousePressEvent(self, event):
        if self._button_rects:
            if self._button_rects[0].contains(event.position()):
                self.dismiss()
                return
            if self._button_rects[1].contains(event.position()):
                self.snooze()
                return
        super().mousePressEvent(event)


class BuddyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumWidth(390)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.focus_seconds = 30 * 60
        self.break_minutes = 5
        self.sound_enabled = True
        self.remaining = self.focus_seconds
        self.paused = False
        self.overlay: CloneOverlay | None = None
        self._build_ui()
        self._build_tray()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)
        self._refresh_timer_label()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)
        title = QLabel("🍥 Desktop Buddy")
        title.setStyleSheet("font-size: 20px; font-weight: 700;")
        root.addWidget(title)
        intro = QLabel("A tiny ninja buddy for breaks, notes, and a little chaos.")
        intro.setWordWrap(True)
        intro.setStyleSheet("color: #666;")
        root.addWidget(intro)

        self.status = QLabel("Naruto is chilling. Keep going, ninja.")
        self.status.setWordWrap(True)
        self.status.setStyleSheet("font-size: 14px; font-weight: 600; padding: 8px; background: #fff1df; border-radius: 8px;")
        root.addWidget(self.status)
        self.timer_label = QLabel()
        self.timer_label.setStyleSheet("font-size: 18px; font-family: Consolas;")
        root.addWidget(self.timer_label)

        settings = QGroupBox("Break settings")
        settings_layout = QVBoxLayout(settings)
        row = QHBoxLayout()
        row.addWidget(QLabel("Focus interval (minutes)"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 180)
        self.interval_spin.setValue(30)
        row.addWidget(self.interval_spin)
        settings_layout.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel("Break duration (minutes)"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 60)
        self.break_spin.setValue(5)
        row.addWidget(self.break_spin)
        settings_layout.addLayout(row)
        self.sound_check = QCheckBox("Enable sound effects")
        self.sound_check.setChecked(True)
        settings_layout.addWidget(self.sound_check)
        root.addWidget(settings)

        buttons = QHBoxLayout()
        apply_button = QPushButton("Start / Apply settings")
        apply_button.clicked.connect(self.apply_settings)
        buttons.addWidget(apply_button)
        self.pause_button = QPushButton("Pause timer")
        self.pause_button.clicked.connect(self.toggle_pause)
        buttons.addWidget(self.pause_button)
        root.addLayout(buttons)

        test_button = QPushButton("Test Shadow Clone Jutsu now")
        test_button.clicked.connect(self.launch_overlay)
        root.addWidget(test_button)
        note = QLabel("Notes and draggable character sprites are planned for a later milestone.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #666;")
        root.addWidget(note)
        exit_button = QPushButton("Exit Desktop Buddy")
        exit_button.clicked.connect(QApplication.instance().quit)
        root.addWidget(exit_button)
        self.setStyleSheet("""
            QWidget { background: #faf8ff; color: #252235; }
            QGroupBox { font-weight: 600; border: 1px solid #d9d2e8; border-radius: 10px; margin-top: 8px; padding: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QPushButton { padding: 9px; border-radius: 8px; background: #ff922e; color: #231526; font-weight: 600; }
            QPushButton:hover { background: #ffad55; }
            QSpinBox { padding: 5px; }
            QCheckBox { padding: 4px; }
        """)

    def _build_tray(self):
        self.tray = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon), self)
        self.tray.setToolTip(APP_NAME)
        menu = QMenu()
        menu.addAction("Show settings", self.showNormal)
        menu.addAction("Test Shadow Clone Jutsu", self.launch_overlay)
        menu.addSeparator()
        menu.addAction("Exit", QApplication.instance().quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self.showNormal()
            if reason == QSystemTrayIcon.ActivationReason.Trigger else None
        )
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def apply_settings(self):
        self.focus_seconds = self.interval_spin.value() * 60
        self.break_minutes = self.break_spin.value()
        self.sound_enabled = self.sound_check.isChecked()
        self.remaining = self.focus_seconds
        self.paused = False
        self.pause_button.setText("Pause timer")
        self.status.setText("Settings applied — believe it! 🍥")
        self._refresh_timer_label()

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.setText("Resume timer" if self.paused else "Pause timer")
        self.status.setText("Timer paused" if self.paused else "Focus session resumed")
        self._refresh_timer_label()

    def _tick(self):
        if self.paused or self.overlay is not None:
            return
        self.remaining -= 1
        if self.remaining <= 0:
            self.launch_overlay()
        self._refresh_timer_label()

    def _refresh_timer_label(self):
        mins, secs = divmod(max(0, self.remaining), 60)
        self.timer_label.setText(f"{mins:02d}:{secs:02d} until Shadow Clone Jutsu")

    def launch_overlay(self):
        if self.overlay is not None:
            self.overlay.raise_()
            self.overlay.activateWindow()
            return
        self.overlay = CloneOverlay(
            self.break_minutes, self.sound_enabled, self._overlay_finished
        )
        self.overlay.showFullScreen()
        self.overlay.raise_()
        self.overlay.activateWindow()
        self.status.setText("Shadow Clone Jutsu! Break time!")

    def _overlay_finished(self, reason: str):
        self.overlay = None
        if reason == "snoozed":
            self.remaining = 5 * 60
            self.status.setText("Snoozed — the clones will return in five minutes.")
        else:
            self.remaining = self.focus_seconds
            self.status.setText("Break finished. Back to your adventure!")
            play_effect(self.sound_enabled, "end")
        self._refresh_timer_label()

    def closeEvent(self, event):
        if self.overlay is not None:
            overlay = self.overlay
            self.overlay = None
            overlay.close()
        if hasattr(self, "tray"):
            self.tray.hide()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(True)
    window = BuddyWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
