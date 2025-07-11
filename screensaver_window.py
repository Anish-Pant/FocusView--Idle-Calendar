# screensaver_window.py

import datetime
import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap, QColor


class ScreensaverWindow(QWidget):
   #Implements the definitive "Glassmorphism" UI, combining a robust card layout with a centralized, maintainable stylesheet.
    
    activity_detected = pyqtSignal()

    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.setWindowTitle("IdleCalendar Screensaver")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setMouseTracking(True)

        # --- Load Background ---
        image_path = 'background.jpg'
        if os.path.exists(image_path):
            self.background_pixmap = QPixmap(image_path)
        else:
            print(f"Warning: Background image not found at '{image_path}'.")
            self.background_pixmap = None
            self.setStyleSheet("background-color: #1A2827;")

        # --- Layouts and Widgets ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(80, 60, 80, 60)
        main_layout.setSpacing(80)
        left_panel_layout = QVBoxLayout()
        left_panel_layout.setSpacing(15)
        right_panel_layout = QVBoxLayout()
        right_panel_layout.setSpacing(15)

        # Create all widgets
        self.clock_label = QLabel()
        self.clock_label.setObjectName("clockLabel")
        self.date_label = QLabel()
        self.date_label.setObjectName("dateLabel")
        next_event_title = QLabel("NEXT EVENT")
        next_event_title.setObjectName("titleLabel")
        self.next_event_summary_label = QLabel("Checking calendar...")
        self.next_event_summary_label.setObjectName("nextEventSummary")
        self.next_event_summary_label.setWordWrap(True)
        self.next_event_time_label = QLabel("")
        self.next_event_time_label.setObjectName("nextEventTime")
        agenda_title = QLabel("LATER TODAY")
        agenda_title.setObjectName("titleLabel")
        self.agenda_items_layout = QVBoxLayout()
        self.agenda_items_layout.setSpacing(10)

        # Assemble Layouts
        left_panel_layout.addItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        left_panel_layout.addWidget(self.clock_label)
        left_panel_layout.addWidget(self.date_label)
        left_panel_layout.addSpacing(40)
        left_panel_layout.addWidget(next_event_title)
        left_panel_layout.addWidget(self.next_event_summary_label)
        left_panel_layout.addWidget(self.next_event_time_label)
        left_panel_layout.addItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        right_panel_layout.addWidget(agenda_title)
        right_panel_layout.addLayout(self.agenda_items_layout)
        right_panel_layout.addStretch()

        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.Shape.VLine)
        separator_line.setObjectName("separatorLine")

        left_frame = QFrame()
        left_frame.setLayout(left_panel_layout)
        right_frame = QFrame()
        right_frame.setLayout(right_panel_layout)

        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(separator_line)
        main_layout.addWidget(right_frame, 1)

        # --- Apply Styles, Timers ---
        self.apply_styles()
        self.apply_shadows()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time_and_date)
        self.clock_timer.start(1000)
        self.update_time_and_date()

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

    def keyPressEvent(self, event): self.activity_detected.emit(); super().keyPressEvent(event)
    def mouseMoveEvent(self, event): self.activity_detected.emit(); super().mouseMoveEvent(event)
    def mousePressEvent(self, event): self.activity_detected.emit(); super().mousePressEvent(event)

    def apply_styles(self):
        """Centralized glass UI stylesheet."""
        glass_panel_style = """
            background-color: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 12px;
        """
        font_family = "'Segoe UI', 'Helvetica', sans-serif"

        self.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                font-family: {font_family};
                background-color: transparent;
            }}
            #clockLabel {{
                font-size: 120px;
                font-weight: 300;
                padding: 10px 25px;
                {glass_panel_style}
            }}
            #dateLabel {{
                font-size: 20px;
                font-weight: 400;
                padding: 8px 15px;
                {glass_panel_style}
            }}
            #titleLabel {{
                font-size: 14px;
                font-weight: 400;
                letter-spacing: 2px;
                padding-bottom: 5px;
                padding-left: 5px;
                border: none;
            }}
            #nextEventSummary {{
                font-size: 36px;
                font-weight: 500;
                padding: 10px 20px;
                {glass_panel_style}
            }}
            #nextEventTime {{
                font-size: 20px;
                font-weight: 400;
                padding: 8px 15px;
                {glass_panel_style}
            }}
            .agendaCard {{
                {glass_panel_style}
            }}
            .agendaSummary {{
                font-size: 18px;
                font-weight: 500;
            }}
            .agendaTime {{
                font-size: 14px;
                color: rgba(220, 220, 220, 0.8);
            }}
            QFrame[objectName="separatorLine"] {{
                background-color: rgba(255, 255, 255, 0.05);
                width: 1px;
            }}
        """)

    def apply_shadows(self):
        """Optional: Apply soft shadows to key UI elements for more depth."""
        def shadow(widget, blur=30, color=QColor(0, 0, 0, 160)):
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(blur)
            effect.setOffset(0, 4)
            effect.setColor(color)
            widget.setGraphicsEffect(effect)

        shadow(self.clock_label)
        shadow(self.date_label)
        shadow(self.next_event_summary_label)
        shadow(self.next_event_time_label)

    def update_time_and_date(self):
        now = datetime.datetime.now()
        self.clock_label.setText(now.strftime("%H:%M"))
        self.date_label.setText(now.strftime("%A, %B %d"))

    def _create_agenda_card(self, event):
        """Helper function to create a single, styled agenda event card."""
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

    def update_events(self, events):
        """Updates the UI with the latest event data using the card layout."""
        for i in reversed(range(self.agenda_items_layout.count())):
            item = self.agenda_items_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        if not events:
            self.next_event_summary_label.setText("No upcoming events")
            self.next_event_time_label.setText("")
            return

        # --- Next Event ---
        first_event = events[0]
        self.next_event_summary_label.setText(first_event['summary'])
        try:
            event_dt = datetime.datetime.fromisoformat(first_event['start']).astimezone()
            relative_str, _ = self.format_relative_time(event_dt)
            self.next_event_time_label.setText(relative_str)
        except (ValueError, TypeError):
            self.next_event_time_label.setText(self.format_event_time(first_event['start']))

        # --- Agenda List ---
        agenda_events = events[1:6]
        for event in agenda_events:
            card = self._create_agenda_card(event)
            self.agenda_items_layout.addWidget(card)

        self.style().unpolish(self)
        self.style().polish(self)

    def format_relative_time(self, dt_event):
        now = datetime.datetime.now().astimezone()
        delta = dt_event - now
        if delta.total_seconds() <= 1: return "starts now", "high"
        days = delta.days
        hours = int(delta.total_seconds() / 3600) % 24
        minutes = int(delta.total_seconds() / 60) % 60
        if days > 1: return f"in {days} days", "low"
        if days == 1: return "in 1 day", "low"
        if hours > 0: return f"in {hours}h {minutes}m", "medium"
        return f"in {minutes} minutes", "high"

    def format_event_time(self, time_str):
        try:
            if 'T' not in time_str:
                return "All Day"
            dt = datetime.datetime.fromisoformat(time_str).astimezone()
            return dt.strftime("%I:%M %p")
        except (ValueError, TypeError):
            return ""
