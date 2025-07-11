
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import idle_monitor
import calendar_service
from screensaver_window import ScreensaverWindow

IDLE_THRESHOLD_SECONDS = 10
CHECK_INTERVAL_SECONDS = 2 

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = ScreensaverWindow()

        # Connect the window's signal to the hide function.
        self.window.activity_detected.connect(self.hide_screensaver_on_activity)

        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self.check_idle_status)
        
        self.calendar_refresh_timer = QTimer()
        self.calendar_refresh_timer.timeout.connect(self.update_calendar_data)

    def run(self):
        print("IdleCalendar started. Monitoring for inactivity...")
        self.main_timer.start(CHECK_INTERVAL_SECONDS * 1000)
        sys.exit(self.app.exec())

    def check_idle_status(self):
        idle_time = idle_monitor.get_idle_time()
        
        # Show Logic (remains the same)
        if idle_time >= IDLE_THRESHOLD_SECONDS and not self.window.isVisible():
            print(f"Idle threshold reached ({idle_time:.0f}s). Showing screensaver.")
            self.update_calendar_data() 
            self.window.showFullScreen()
            self.calendar_refresh_timer.start(15 * 60 * 1000) 

        # The polling-based hide logic is now just a fallback.
        # The primary hide mechanism is the event-driven one below.
        elif idle_time < 1 and self.window.isVisible():
             self.hide_screensaver_on_activity()


    #  This function is called INSTANTLY by the signal from the window.
    def hide_screensaver_on_activity(self):
        # We only need to act if the window is actually visible.
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