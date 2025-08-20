import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from ui_main_window import MainWindow
from update_dialog import UpdateNotifier


def main():
    app = QApplication(sys.argv)
    
    # Set application icon for taskbar - try multiple approaches
    # Try ICO first (better Windows compatibility), then PNG as fallback
    icon_path = os.path.join(os.path.dirname(__file__), "svgs", "logo.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(os.path.dirname(__file__), "svgs", "logo.png")
    
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
        # Also try setting it as the application icon
        app.setProperty("windowIcon", icon)
    
    window = MainWindow()
    window.show()
    
    # Force refresh the window icon
    window.setWindowIcon(window.windowIcon())
    
    # Initialize auto-update checker
    update_notifier = UpdateNotifier(window)
    
    # Check for updates after a short delay (to let the app load first)
    QTimer.singleShot(3000, lambda: update_notifier.check_for_updates())
    
    # Check for updates every 24 hours
    update_timer = QTimer()
    update_timer.timeout.connect(lambda: update_notifier.check_for_updates())
    update_timer.start(24 * 60 * 60 * 1000)  # 24 hours in milliseconds
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()



