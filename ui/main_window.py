import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

import psutil

class VisualizerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.amplitude = 0.0

        # Smooth animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_visualizer)
        self.anim_timer.start(30) # ~33fps
        self.target_amplitude = 0.0
        self.is_listening = False

    def set_amplitude(self, amp: float):
        self.target_amplitude = min(amp, 1.0)

    def set_listening_state(self, state: bool):
        self.is_listening = state
        if not state:
            self.target_amplitude = 0.0

    def update_visualizer(self):
        # Smooth transition to target amplitude
        diff = self.target_amplitude - self.amplitude
        self.amplitude += diff * 0.2

        if self.is_listening and self.target_amplitude == 0.0:
            # Add a slight idle pulse when listening but no sound
            import math
            import time
            pulse = (math.sin(time.time() * 5) + 1) * 0.1
            self.amplitude = pulse

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Base ring
        base_radius = 50
        # Expand based on amplitude
        current_radius = base_radius + (self.amplitude * 50)

        # Color based on state
        color = QColor(0, 255, 255) if self.is_listening else QColor(100, 100, 100)

        pen = QPen(color, 4)
        painter.setPen(pen)

        # Glow effect
        glow_color = QColor(color)
        glow_color.setAlpha(50)
        painter.setBrush(QBrush(glow_color))

        painter.drawEllipse(center_x - current_radius, center_y - current_radius,
                            current_radius * 2, current_radius * 2)

class MetricWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0%")

        self.cpu_label.setStyleSheet("color: #00ffff; font-family: monospace; font-size: 14px;")
        self.ram_label.setStyleSheet("color: #00ffff; font-family: monospace; font-size: 14px;")

        layout.addWidget(self.cpu_label)
        layout.addWidget(self.ram_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(2000) # Update every 2 seconds

    def update_metrics(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.ram_label.setText(f"RAM: {ram}%")

class MainWindow(QWidget):
    # Signals to communicate with main application logic
    push_to_talk_started = Signal()
    push_to_talk_ended = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis AI")
        self.setStyleSheet("background-color: #0a0a0a; color: white;")
        self.resize(400, 600)

        layout = QVBoxLayout(self)

        # Top metrics
        top_layout = QHBoxLayout()
        self.metrics = MetricWidget()
        top_layout.addWidget(self.metrics)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # Central visualizer
        self.visualizer = VisualizerWidget()
        layout.addWidget(self.visualizer, alignment=Qt.AlignCenter)

        # Status Label
        self.status_label = QLabel("Idle")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.status_label)

        # PTT Button
        self.ptt_button = QPushButton("PUSH TO TALK (Spacebar)")
        self.ptt_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #00ffff;
                border-radius: 10px;
                color: #00ffff;
                font-weight: bold;
                padding: 15px;
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: #00ffff;
                color: #000000;
            }
        """)

        self.ptt_button.pressed.connect(self.on_ptt_pressed)
        self.ptt_button.released.connect(self.on_ptt_released)
        layout.addWidget(self.ptt_button)

        self.is_pressing = False

    def on_ptt_pressed(self):
        if not self.is_pressing:
            self.is_pressing = True
            self.status_label.setText("Listening...")
            self.status_label.setStyleSheet("color: #00ffff; font-size: 16px; font-weight: bold;")
            self.visualizer.set_listening_state(True)
            self.push_to_talk_started.emit()

    def on_ptt_released(self):
        if self.is_pressing:
            self.is_pressing = False
            self.status_label.setText("Processing...")
            self.status_label.setStyleSheet("color: #ffff00; font-size: 16px; font-weight: bold;")
            self.visualizer.set_listening_state(False)
            self.push_to_talk_ended.emit()

    from PySide6.QtCore import Slot
    @Slot(str)
    def set_status(self, status: str):
        self.status_label.setText(status)
        if status == "Idle":
            self.status_label.setStyleSheet("color: #888888; font-size: 16px; font-weight: bold;")
        elif status == "Speaking":
            self.status_label.setStyleSheet("color: #00ff00; font-size: 16px; font-weight: bold;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.on_ptt_pressed()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.on_ptt_released()
