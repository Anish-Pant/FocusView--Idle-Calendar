# main.py

import sys
import time
import webbrowser
from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtCore import QTimer, Qt, QObject, QEvent

import idle_monitor
import calendar_service
from screensaver_window import ScreensaverWindow

IDLE_THRESHOLD_SECONDS = 10
CHECK_INTERVAL_SECONDS = 2

# --- Global State Flags ---
snooze_until = 0
postpone_until_next_event = False
session_closed = False
completed_events = set()


class ActivityFilter(QObject):
    """
    Event filter that suppresses right-clicks and Alt presses from being treated
    as 'activity' that hides the overlay. It also asks controller to show the
    context menu when those inputs are detected.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def eventFilter(self, obj, event):
        # Right-click: show context menu at the pointer and prevent hide.
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton:
            # Set a short grace period so the idle checker doesn't hide immediately.
            self.controller.ignore_activity_until = time.time() + 3.0
            # Show context menu using the event's global position
            try:
                self.controller.show_context_menu(event)
            except Exception:
                # fallback: show centered if something goes wrong
                self.controller.show_context_menu_at_center()
            return True  # stop further processing (prevents activity hide)

        # Alt key pressed: show context menu centered and prevent hide.
        if event.type() == QEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Alt, Qt.Key.Key_AltGr):
            self.controller.ignore_activity_until = time.time() + 3.0
            self.controller.show_context_menu_at_center()
            return True  # stop further processing

        return False  # other events are processed normally


class AppController:
    """The main controller that orchestrates the application's logic."""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ScreensaverWindow()
        self.window.activity_detected.connect(self.hide_screensaver_on_activity)

        # Track a timestamp until which idle-based hides will be ignored
        self.ignore_activity_until = 0.0

        # Add custom event filter to capture right-clicks and Alt presses
        self.filter = ActivityFilter(self)
        self.window.installEventFilter(self.filter)

        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self.check_idle_status)

        self.calendar_refresh_timer = QTimer()
        self.calendar_refresh_timer.timeout.connect(self.update_calendar_data)

        self.current_events = []

    def run(self):
        print("FocusView started. Monitoring for inactivity...")
        self.main_timer.start(CHECK_INTERVAL_SECONDS * 1000)
        sys.exit(self.app.exec())

    def check_idle_status(self):
        global snooze_until, postpone_until_next_event, session_closed

        if session_closed or time.time() < snooze_until or postpone_until_next_event:
            return

        idle_time = idle_monitor.get_idle_time()
        is_window_visible = self.window.isVisible()

        # --- Show Logic ---
        if idle_time >= IDLE_THRESHOLD_SECONDS and not is_window_visible:
            print(f"Idle threshold reached ({idle_time:.0f}s). Showing screensaver.")
            self.update_calendar_data()
            self.window.update_idle_timer(idle_time)
            self.window.showFullScreen()
            self.calendar_refresh_timer.start(15 * 60 * 1000)

        elif idle_time >= IDLE_THRESHOLD_SECONDS and is_window_visible:
            self.window.update_idle_timer(idle_time)

        # --- Hide Logic ---
        elif idle_time < 1 and is_window_visible:
            # Respect the grace period after filtered inputs (right-click / Alt)
            if time.time() < self.ignore_activity_until:
                # Debug info to help if you still see hides: extend or log
                # print("Ignoring idle-based hide due to recent filtered input.")
                return
            self.hide_screensaver_on_activity()

    def hide_screensaver_on_activity(self):
        if self.window.isVisible():
            print("Activity event detected. Hiding screensaver instantly.")
            self.window.hide()
            self.calendar_refresh_timer.stop()

    def update_calendar_data(self):
        print("Fetching latest calendar events...")
        events = calendar_service.get_upcoming_events()
        self.current_events = events
        self.window.update_events(events)

    # --- Context Menu Logic ---
    def show_context_menu(self, event_or_qt_event):
        """
        Accept either the QContextMenuEvent-like object from the filter (it has globalPos())
        or a QEvent passed explicitly. We'll extract globalPos() if available.
        """
        global snooze_until, postpone_until_next_event, session_closed

        pos = None
        try:
            # event may be a Qt event object with globalPos()
            pos = event_or_qt_event.globalPos()
        except Exception:
            pos = None

        menu = QMenu(self.window)
        menu.addAction("Snooze 5 min", lambda: self.snooze_overlay(5))
        menu.addAction("Snooze 10 min", lambda: self.snooze_overlay(10))
        menu.addAction("Snooze 15 min", lambda: self.snooze_overlay(15))
        menu.addSeparator()
        menu.addAction("Postpone until next event", self.postpone_overlay)
        menu.addAction("Mark current event as done", self.mark_done)
        menu.addAction("Open in Google Calendar", self.open_calendar)
        menu.addSeparator()
        menu.addAction("Close overlay for session", self.close_for_session)

        # If we have a global pos, use it; otherwise show centered on window
        if pos:
            menu.exec(pos)
        else:
            self.show_menu_centered(menu)

    def show_context_menu_at_center(self):
        """Helper to show a context menu centered within the screensaver window."""
        menu = QMenu(self.window)
        menu.addAction("Snooze 5 min", lambda: self.snooze_overlay(5))
        menu.addAction("Snooze 10 min", lambda: self.snooze_overlay(10))
        menu.addAction("Snooze 15 min", lambda: self.snooze_overlay(15))
        menu.addSeparator()
        menu.addAction("Postpone until next event", self.postpone_overlay)
        menu.addAction("Mark current event as done", self.mark_done)
        menu.addAction("Open in Google Calendar", self.open_calendar)
        menu.addSeparator()
        menu.addAction("Close overlay for session", self.close_for_session)
        self.show_menu_centered(menu)

    def show_menu_centered(self, menu: QMenu):
        """Exec the menu centered inside the window."""
        try:
            center_point = self.window.mapToGlobal(self.window.rect().center())
            menu.exec(center_point)
        except Exception:
            # last resort: exec without a position
            menu.exec()

    def snooze_overlay(self, minutes):
        global snooze_until
        snooze_until = time.time() + minutes * 60
        print(f"Overlay snoozed for {minutes} minutes.")
        self.hide_screensaver_on_activity()

    def postpone_overlay(self):
        global postpone_until_next_event
        postpone_until_next_event = True
        print("Overlay postponed until next calendar event.")
        self.hide_screensaver_on_activity()

    def mark_done(self):
        global completed_events
        if self.current_events:
            completed_events.add(self.current_events[0]['id'])
            print(f"Event marked as done: {self.current_events[0]['summary']}")
        self.hide_screensaver_on_activity()

    def open_calendar(self):
        if self.current_events:
            url = self.current_events[0].get('htmlLink')
            if url:
                print(f"Opening calendar event: {url}")
                webbrowser.open(url)

    def close_for_session(self):
        global session_closed
        session_closed = True
        print("Overlay closed for session.")
        self.hide_screensaver_on_activity()


if __name__ == '__main__':
    import os
    if not os.path.exists(calendar_service.TOKEN_FILE):
        print(f"Error: '{calendar_service.TOKEN_FILE}' not found!")
        print("Please run 'python authenticate.py' once to log in and authorize the application.")
        sys.exit(1)

    controller = AppController()
    controller.run()
