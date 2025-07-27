
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel

import idle_monitor
import calendar_service
from screensaver_window import ScreensaverWindow

IDLE_THRESHOLD_SECONDS = 10
CHECK_INTERVAL_SECONDS = 2 

class AppController:
    """
    The main controller that orchestrates the application's logic.
    """
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ScreensaverWindow()
        self.window.activity_detected.connect(self.hide_screensaver_on_activity)

        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self.check_idle_status)
        
        self.calendar_refresh_timer = QTimer()
        self.calendar_refresh_timer.timeout.connect(self.update_calendar_data)

    def run(self):
        print("FocusView started. Monitoring for inactivity...")
        self.main_timer.start(CHECK_INTERVAL_SECONDS * 1000)
        sys.exit(self.app.exec())

    def check_idle_status(self):
        """The core logic loop, triggered by the main_timer."""
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
             self.hide_screensaver_on_activity()

    def hide_screensaver_on_activity(self):
        if self.window.isVisible():
            print("Activity event detected. Hiding screensaver instantly.")
            self.window.hide()
            self.calendar_refresh_timer.stop()

    def update_calendar_data(self):
        print("Fetching latest calendar events...")
        events = calendar_service.get_upcoming_events()
        self.window.update_events(events)

if __name__ == '__main__':
    import os
    if not os.path.exists(calendar_service.TOKEN_FILE):
        print(f"Error: '{calendar_service.TOKEN_FILE}' not found!")
        print("Please run 'python authenticate.py' once to log in and authorize the application.")
        sys.exit(1)

    controller = AppController()
    controller.run()