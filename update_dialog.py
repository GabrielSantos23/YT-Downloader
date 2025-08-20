import os
import sys
from pathlib import Path
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QTextEdit, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from github_release_manager import GitHubReleaseManager, UpdateDownloaderThread

class UpdateDialog(QDialog):
    """Dialog for handling application updates"""
    
    def __init__(self, parent=None, version="", download_url=""):
        super().__init__(parent)
        self.version = version
        self.download_url = download_url
        self.release_manager = GitHubReleaseManager()
        self.download_thread = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Update Available")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Center window
        self.setGeometry(
            (self.screen().availableGeometry().width() - 500) // 2,
            (self.screen().availableGeometry().height() - 400) // 2,
            500, 400
        )
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("🎉 New Update Available!")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        version_label = QLabel(f"Version {self.version} is now available")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        current_version = QLabel(f"Current version: {self.release_manager.CURRENT_VERSION}")
        current_version.setFont(QFont("Arial", 10))
        current_version.setAlignment(Qt.AlignCenter)
        layout.addWidget(current_version)
        
        # Description
        desc_label = QLabel("This update includes bug fixes and improvements.")
        desc_label.setFont(QFont("Arial", 10))
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.update_btn = QPushButton("Update Now")
        self.update_btn.clicked.connect(self.start_update)
        button_layout.addWidget(self.update_btn)
        
        self.later_btn = QPushButton("Remind Me Later")
        self.later_btn.clicked.connect(self.remind_later)
        button_layout.addWidget(self.later_btn)
        
        self.skip_btn = QPushButton("Skip This Version")
        self.skip_btn.clicked.connect(self.skip_version)
        button_layout.addWidget(self.skip_btn)
        
        layout.addLayout(button_layout)
    
    def log(self, message: str):
        """Add message to status text"""
        self.status_text.append(f"[{self.get_timestamp()}] {message}")
        self.status_text.ensureCursorVisible()
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def start_update(self):
        """Start the update process"""
        self.update_btn.setEnabled(False)
        self.later_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        
        # Show progress elements
        self.progress_bar.setVisible(True)
        self.status_text.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.log("Starting update download...")
        
        # Start download thread
        self.download_thread = UpdateDownloaderThread(self.release_manager, self.download_url)
        self.download_thread.progress_updated.connect(self.progress_bar.setValue)
        self.download_thread.download_finished.connect(self.on_download_finished)
        self.download_thread.start()
    
    def on_download_finished(self, success: bool, message: str):
        """Handle download completion"""
        if success:
            self.log("✅ Download completed successfully!")
            self.log("Applying update...")
            
            # Apply the update
            if self.release_manager.apply_update():
                self.log("✅ Update applied successfully!")
                
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Update Complete")
                msg.setText("Update has been applied successfully!")
                msg.setInformativeText("The application will restart to apply the changes.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                
                # Restart the application
                self.restart_application()
            else:
                self.log("❌ Failed to apply update")
                self.show_error("Failed to apply update. Please try again or download manually.")
        else:
            self.log(f"❌ Download failed: {message}")
            self.show_error(f"Download failed: {message}")
        
        # Re-enable buttons
        self.update_btn.setEnabled(True)
        self.later_btn.setEnabled(True)
        self.skip_btn.setEnabled(True)
    
    def restart_application(self):
        """Restart the application"""
        try:
            # Get the current executable path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                exe_path = sys.executable
            else:
                # Running as script
                exe_path = sys.executable
                script_path = Path(__file__).parent / "main.py"
                if script_path.exists():
                    exe_path = f'"{exe_path}" "{script_path}"'
            
            # Start new process
            import subprocess
            subprocess.Popen([exe_path], shell=True)
            
            # Close current application
            self.accept()
            QTimer.singleShot(100, lambda: sys.exit(0))
            
        except Exception as e:
            print(f"Error restarting application: {e}")
            self.show_error("Please restart the application manually to apply the update.")
    
    def remind_later(self):
        """Remind user later"""
        self.accept()
    
    def skip_version(self):
        """Skip this version"""
        # Save skipped version to avoid showing again
        self.save_skipped_version()
        self.accept()
    
    def save_skipped_version(self):
        """Save the skipped version to avoid showing again"""
        try:
            config_dir = Path(__file__).parent / "config"
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "update_config.json"
            config = {}
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            config['skipped_version'] = self.version
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving skipped version: {e}")
    
    def show_error(self, message: str):
        """Show error message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Update Error")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


class UpdateNotifier:
    """Handles background update checking and notification"""
    
    def __init__(self, parent_widget=None):
        self.parent = parent_widget
        self.release_manager = GitHubReleaseManager()
        self.update_checker = None
        self.last_check_time = None
    
    def check_for_updates(self, show_dialog=True):
        """Check for updates in background"""
        # Don't check too frequently
        from datetime import datetime, timedelta
        if (self.last_check_time and 
            datetime.now() - self.last_check_time < timedelta(hours=1)):
            return
        
        self.last_check_time = datetime.now()
        
        # Start background check
        self.update_checker = UpdateCheckerThread(self.release_manager)
        self.update_checker.update_found.connect(
            lambda version, url: self.on_update_found(version, url, show_dialog)
        )
        self.update_checker.check_completed.connect(self.on_check_completed)
        self.update_checker.start()
    
    def on_update_found(self, version: str, download_url: str, show_dialog: bool):
        """Handle when an update is found"""
        # Check if this version was skipped
        if self.is_version_skipped(version):
            return
        
        if show_dialog and self.parent:
            # Show update dialog
            dialog = UpdateDialog(self.parent, version, download_url)
            dialog.exec()
    
    def on_check_completed(self, success: bool):
        """Handle when update check completes"""
        if not success:
            print("Update check completed with errors")
    
    def is_version_skipped(self, version: str) -> bool:
        """Check if this version was previously skipped"""
        try:
            config_file = Path(__file__).parent / "config" / "update_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('skipped_version') == version
        except Exception as e:
            print(f"Error checking skipped version: {e}")
        
        return False


# Import json for the skipped version functionality
import json
