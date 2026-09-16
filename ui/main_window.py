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
        self.anim_timer.start(50) # ~20fps for performance optimization
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
        base_radius = 60
        # Expand based on amplitude
        current_radius = base_radius + (self.amplitude * 70)

        # Color based on state (Neon Cyan vs Obsidian Grey)
        color = QColor(0, 255, 255) if self.is_listening else QColor(40, 50, 60)

        # Inner Ring
        pen = QPen(color, 2)
        painter.setPen(pen)
        painter.drawEllipse(center_x - base_radius, center_y - base_radius, base_radius * 2, base_radius * 2)

        # Outer Reactive Ring
        pen = QPen(color, 5)
        painter.setPen(pen)

        # Glow effect
        glow_color = QColor(color)
        glow_color.setAlpha(60)
        painter.setBrush(QBrush(glow_color))

        painter.drawEllipse(center_x - current_radius, center_y - current_radius,
                            current_radius * 2, current_radius * 2)

class MetricWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0%")

        self.cpu_label.setStyleSheet("color: #00ffff; font-family: 'Courier New', monospace; font-size: 14px; background: rgba(0, 20, 30, 0.6); padding: 5px; border-radius: 4px; border: 1px solid #005577;")
        self.ram_label.setStyleSheet("color: #00ffff; font-family: 'Courier New', monospace; font-size: 14px; background: rgba(0, 20, 30, 0.6); padding: 5px; border-radius: 4px; border: 1px solid #005577;")

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
        self.setWindowTitle("Jarvis Terminal")
        self.setStyleSheet("""
            QWidget {
                background-color: #050a0f;
                color: #e0f2fe;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
            }
        """)
        self.resize(450, 700)

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
        self.status_label = QLabel("Bekliyor")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
                padding: 10px;
                background: rgba(0, 255, 255, 0.05);
                border-radius: 8px;
                border: 1px solid rgba(0, 255, 255, 0.1);
            }
        """)
        layout.addWidget(self.status_label)

        # PTT Button
        self.ptt_button = QPushButton("DİNLE (Boşluk Tuşu)")
        self.ptt_button.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #082f49, stop:1 #0c4a6e);
                border: 2px solid #00ffff;
                border-radius: 12px;
                color: #22d3ee;
                font-weight: bold;
                letter-spacing: 1.5px;
                padding: 18px;
                font-size: 16px;
            }
            QPushButton:pressed {
                background-color: #00ffff;
                color: #020617;
                border: 2px solid #ffffff;
            }
            QPushButton:hover {
                border: 2px solid #67e8f9;
            }
        """)

        self.ptt_button.pressed.connect(self.on_ptt_pressed)
        self.ptt_button.released.connect(self.on_ptt_released)
        layout.addWidget(self.ptt_button)

        self.is_pressing = False

    def on_ptt_pressed(self):
        if not self.is_pressing:
            self.is_pressing = True
            self.set_status("Dinliyor...")
            self.visualizer.set_listening_state(True)
            self.push_to_talk_started.emit()

    def on_ptt_released(self):
        if self.is_pressing:
            self.is_pressing = False
            self.set_status("İşleniyor...")
            self.visualizer.set_listening_state(False)
            self.push_to_talk_ended.emit()

    from PySide6.QtCore import Slot
    @Slot(str)
    def set_status(self, status: str):
        self.status_label.setText(status.upper())
        base_style = """
            QLabel {
                font-size: 18px;
                font-weight: 800;
                letter-spacing: 2px;
                padding: 10px;
                border-radius: 8px;
        """
        if status == "Bekliyor":
            self.status_label.setStyleSheet(base_style + """
                color: #475569;
                background: rgba(0, 255, 255, 0.05);
                border: 1px solid rgba(0, 255, 255, 0.1);
            }""")
        elif status == "Konuşuyor" or status == "Konuşuyor...":
            self.status_label.setStyleSheet(base_style + """
                color: #4ade80;
                background: rgba(74, 222, 128, 0.1);
                border: 1px solid rgba(74, 222, 128, 0.4);
            }""")
        elif status == "Dinliyor...":
            self.status_label.setStyleSheet(base_style + """
                color: #22d3ee;
                background: rgba(34, 211, 238, 0.15);
                border: 1px solid rgba(34, 211, 238, 0.6);
            }""")
        elif status == "İşleniyor..." or status == "Düşünüyor...":
            self.status_label.setStyleSheet(base_style + """
                color: #facc15;
                background: rgba(250, 204, 21, 0.1);
                border: 1px solid rgba(250, 204, 21, 0.4);
            }""")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.on_ptt_pressed()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.on_ptt_released()
