#!/usr/bin/env python3
"""
Simple test script to demonstrate the loading button functionality.
"""

import sys
import time
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer

from loading_widget import LoadingButton


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Button Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create loading buttons
        self.search_btn = LoadingButton("Search")
        self.search_btn.setFixedSize(100, 40)
        self.search_btn.clicked.connect(self.start_search)
        
        self.download_btn = LoadingButton("Download")
        self.download_btn.setFixedSize(100, 40)
        self.download_btn.clicked.connect(self.start_download)
        
        # Create regular button to stop loading
        self.stop_btn = QPushButton("Stop All")
        self.stop_btn.clicked.connect(self.stop_all)
        
        # Add buttons to layout
        layout.addWidget(self.search_btn)
        layout.addWidget(self.download_btn)
        layout.addWidget(self.stop_btn)
        layout.addStretch()
        
        # Setup timers for demo
        self.search_timer = QTimer()
        self.search_timer.timeout.connect(self.stop_search)
        self.search_timer.setSingleShot(True)
        
        self.download_timer = QTimer()
        self.download_timer.timeout.connect(self.stop_download)
        self.download_timer.setSingleShot(True)
    
    def start_search(self):
        """Start the search loading animation."""
        print("Starting search...")
        self.search_btn.setLoading(True)
        self.search_timer.start(3000)  # Stop after 3 seconds
    
    def stop_search(self):
        """Stop the search loading animation."""
        print("Search completed!")
        self.search_btn.setLoading(False)
    
    def start_download(self):
        """Start the download loading animation."""
        print("Starting download...")
        self.download_btn.setLoading(True)
        self.download_timer.start(5000)  # Stop after 5 seconds
    
    def stop_download(self):
        """Stop the download loading animation."""
        print("Download completed!")
        self.download_btn.setLoading(False)
    
    def stop_all(self):
        """Stop all loading animations."""
        print("Stopping all...")
        self.search_btn.setLoading(False)
        self.download_btn.setLoading(False)
        self.search_timer.stop()
        self.download_timer.stop()


def main():
    app = QApplication(sys.argv)
    
    # Apply dark stylesheet
    from style import dark_stylesheet
    app.setStyleSheet(dark_stylesheet())
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


