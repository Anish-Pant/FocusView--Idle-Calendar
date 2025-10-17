# screensaver_window.py

import datetime
import os
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap


class ScreensaverWindow(QWidget):
    activity_detected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FocusView")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setMouseTracking(True)

        image_path = 'background.jpg'
        if os.path.exists(image_path):
            self.background_pixmap = QPixmap(image_path)
        else:
            self.background_pixmap = None
            self.setStyleSheet("background-color: #1A2827;")

        # --- Layouts ---
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Main horizontal layout for hybrid
        main_content_widget = QWidget(self)
        main_content_layout = QHBoxLayout(main_content_widget)
        main_content_layout.setContentsMargins(80, 60, 80, 60)
        main_content_layout.setSpacing(80)
        window_layout.addStretch(1)
        window_layout.addWidget(main_content_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        window_layout.addStretch(1)
        self.idle_timer_label = QLabel(self)
        self.idle_timer_label.setObjectName("idleTimerLabel")

        # --- Widgets ---
        self.clock_label = QLabel()
        self.date_label = QLabel()
        self.next_event_summary_label = QLabel("Checking calendar...")
        self.next_event_summary_label.setWordWrap(True)
        self.next_event_time_label = QLabel("")

        # Left panel (centered main content)
        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(30)
        left_panel_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Time and date in one card
        time_date_card = QFrame()
        time_date_card.setObjectName("glassCard")
        time_date_layout = QVBoxLayout(time_date_card)
        time_date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clock_label.setObjectName("clockLabel")
        self.date_label.setObjectName("dateLabel")
        time_date_layout.addWidget(self.clock_label, alignment=Qt.AlignmentFlag.AlignCenter)
        time_date_layout.addWidget(self.date_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Next event in one card
        next_event_card = QFrame()
        next_event_card.setObjectName("glassCard")
        next_event_layout = QVBoxLayout(next_event_card)
        next_event_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.next_event_summary_label.setObjectName("nextEventSummary")
        self.next_event_time_label.setObjectName("nextEventTime")
        next_event_layout.addWidget(self.next_event_summary_label, alignment=Qt.AlignmentFlag.AlignCenter)
        next_event_layout.addWidget(self.next_event_time_label, alignment=Qt.AlignmentFlag.AlignCenter)

        left_panel_layout.addWidget(time_date_card, alignment=Qt.AlignmentFlag.AlignCenter)
        left_panel_layout.addWidget(next_event_card, alignment=Qt.AlignmentFlag.AlignCenter)
        left_panel_layout.addStretch()

        # Right panel (agenda)
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setSpacing(15)
        right_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        agenda_title = QLabel("LATER TODAY")
        agenda_title.setObjectName("titleLabel")
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 2)
        shadow.setColor(Qt.GlobalColor.black)
        agenda_title.setGraphicsEffect(shadow)
        right_panel_layout.addWidget(agenda_title, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.agenda_items_layout = QVBoxLayout()
        self.agenda_items_layout.setSpacing(10)
        agenda_items_widget = QWidget()
        agenda_items_widget.setLayout(self.agenda_items_layout)
        right_panel_layout.addWidget(agenda_items_widget)
        right_panel_layout.addStretch()

        # Add panels to main content
        main_content_layout.addLayout(left_panel_layout, 2)
        main_content_layout.addLayout(right_panel_layout, 1)

        # --- Apply Styles & Timers ---
        self.apply_styles()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time_and_date)
        self.clock_timer.start(1000)
        self.update_time_and_date()

    # --- Event Handlers ---
    def keyPressEvent(self, event):
        """Ignore Alt key so it can be used for menu actions."""
        key = event.key()
        if key in (Qt.Key.Key_Alt, Qt.Key.Key_AltGr):
            event.accept()
            return
        # all other keys count as activity
        self.activity_detected.emit()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Ignore right-clicks to allow context menu."""
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return
        # Left and middle clicks count as activity
        self.activity_detected.emit()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Mouse movement still counts as activity."""
        self.activity_detected.emit()
        super().mouseMoveEvent(event)

    # --- Painting & Layout ---
    def paintEvent(self, event):
        if self.background_pixmap:
            painter = QPainter(self)
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            point = self.rect().center() - scaled_pixmap.rect().center()
            painter.drawPixmap(point, scaled_pixmap)
        super().paintEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = self.width() - self.idle_timer_label.width() - 20
        y = self.height() - self.idle_timer_label.height() - 20
        self.idle_timer_label.move(x, y)

    # --- UI Updates ---
    def apply_styles(self):
        font_family = "'Segoe UI', 'Helvetica', sans-serif"
        self.setStyleSheet(f"""
            #glassCard, .agendaCard {{
                background-color: rgba(0, 0, 0, 0.35);
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 12px;
                padding: 15px;
            }}
            QLabel {{
                color: #FFFFFF;
                font-family: {font_family};
                background-color: transparent;
                border: none;
                padding: 0;
            }}
            #clockLabel {{
                font-size: 220px; 
                font-weight: 400;
            }}
            #dateLabel {{
                font-size: 36px;
                font-weight: 400;
            }}
            #titleLabel {{
                font-size: 32px;
                font-weight: 700; 
                color: #FFFFFF;   
                letter-spacing: 2px;
                padding-bottom: 12px;
                padding-left: 5px;
                background-color: rgba(0,0,0,0.5);
                border-radius: 8px;
            }}
            #nextEventSummary {{ font-size: 36px; font-weight: 500; }}
            #nextEventTime {{ font-size: 28px; font-weight: 400; }}
            #idleTimerLabel {{ font-size: 32px; font-weight: 600; color: rgba(255, 255, 255, 0.95); }}
            .agendaSummary {{ font-size: 18px; font-weight: 500; }}
            .agendaTime {{ font-size: 14px; color: #CCCCCC; }}
            QFrame[frameShape="5"] {{ color: rgba(255, 255, 255, 0.2); }}
        """)

    def update_time_and_date(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%A, %B %d"))

    def _create_agenda_card(self, event):
        card = QFrame()
        card.setProperty("class", "agendaCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        layout.setContentsMargins(12, 10, 12, 10)
        summary_label = QLabel(event['summary'])
        summary_label.setProperty("class", "agendaSummary")
        time_label = QLabel(self.format_event_time(event['start']))
        time_label.setProperty("class", "agendaTime")
        layout.addWidget(summary_label)
        layout.addWidget(time_label)
        return card

    def update_idle_timer(self, seconds):
        self.idle_timer_label.setText(self.format_idle_time(seconds))
        self.idle_timer_label.adjustSize()

    def update_events(self, events):
        for i in reversed(range(self.agenda_items_layout.count())):
            item = self.agenda_items_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        if not events:
            self.next_event_summary_label.setText("No upcoming events")
            self.next_event_time_label.setText("")
            return

        first_event = events[0]
        self.next_event_summary_label.setText(first_event['summary'])
        try:
            event_dt = datetime.datetime.fromisoformat(first_event['start']).astimezone()
            relative_str, _ = self.format_relative_time(event_dt)
            self.next_event_time_label.setText(relative_str)
        except (ValueError, TypeError):
            self.next_event_time_label.setText(self.format_event_time(first_event['start']))

        agenda_events = events[1:6]
        for event in agenda_events:
            card = self._create_agenda_card(event)
            self.agenda_items_layout.addWidget(card)

        self.style().unpolish(self)
        self.style().polish(self)

    # --- Helper Functions ---
    def format_idle_time(self, total_seconds):
        total_seconds = int(total_seconds)
        if total_seconds < 60:
            return f"Away for {total_seconds} seconds"
        minutes = total_seconds // 60
        return f"Away for {minutes} minutes"

    def format_relative_time(self, dt_event):
        now = datetime.datetime.now().astimezone()
        delta = dt_event - now
        if delta.total_seconds() <= 1:
            return "starts now", "high"
        days, hours, minutes = delta.days, int(delta.total_seconds() / 3600) % 24, int(delta.total_seconds() / 60) % 60
        if days > 1:
            return f"in {days} days", "low"
        if days == 1:
            return "in 1 day", "low"
        if hours > 0:
            return f"in {hours}h {minutes}m", "medium"
        return f"in {minutes} minutes", "high"

    def format_event_time(self, time_str):
        try:
            if 'T' not in time_str:
                return "All Day"
            dt = datetime.datetime.fromisoformat(time_str).astimezone()
            return dt.strftime("%I:%M %p")
        except (ValueError, TypeError):
            return ""
