import os
import sys
import shutil
import subprocess
import zipfile
import requests
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLabel, QPushButton, QProgressBar, QMessageBox,
                               QTextEdit, QCheckBox)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont, QIcon

class FFmpegDownloader(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, install_dir: Path):
        super().__init__()
        self.install_dir = install_dir
        self.ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip"
    
    def run(self):
        try:
            self.status.emit("Creating installation directory...")
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            zip_path = self.install_dir / "ffmpeg.zip"
            
            self.status.emit("Downloading FFmpeg...")
            self._download_ffmpeg(zip_path)
            
            self.status.emit("Extracting FFmpeg...")
            bin_dir = self._extract_ffmpeg(zip_path)
            
            if bin_dir and (bin_dir / "ffmpeg.exe").exists():
                self.finished.emit(True, str(bin_dir))
            else:
                self.finished.emit(False, "FFmpeg binary not found after extraction")
                
        except Exception as e:
            self.finished.emit(False, str(e))
    
    def _download_ffmpeg(self, zip_path: Path):
        with requests.get(self.ffmpeg_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            written = 0
            
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        written += len(chunk)
                        if total > 0:
                            progress = int((written / total) * 100)
                            self.progress.emit(progress)
    
    def _extract_ffmpeg(self, zip_path: Path):
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(self.install_dir)
        
        for root, dirs, files in os.walk(self.install_dir):
            if "ffmpeg.exe" in files:
                return Path(root)
        return None

class InstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ffmpeg_downloader = None
        self.setup_ui()
        self.check_ffmpeg()
    
    def setup_ui(self):
        self.setWindowTitle("YouTube Downloader - Installer")
        self.setFixedSize(600, 400)
        
        self.setGeometry(
            (self.screen().availableGeometry().width() - 600) // 2,
            (self.screen().availableGeometry().height() - 400) // 2,
            600, 400
        )
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("YouTube Downloader Setup")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.status_label = QLabel("Checking system requirements...")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        button_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("Install FFmpeg")
        self.install_btn.setVisible(False)
        self.install_btn.clicked.connect(self.install_ffmpeg)
        button_layout.addWidget(self.install_btn)
        
        self.skip_btn = QPushButton("Skip (Install Later)")
        self.skip_btn.setVisible(False)
        self.skip_btn.clicked.connect(self.skip_ffmpeg)
        button_layout.addWidget(self.skip_btn)
        
        self.finish_btn = QPushButton("Finish Setup")
        self.finish_btn.setVisible(False)
        self.finish_btn.clicked.connect(self.finish_setup)
        button_layout.addWidget(self.finish_btn)
        
        layout.addLayout(button_layout)
    
    def log(self, message: str):
        self.log_text.append(f"[{self.get_timestamp()}] {message}")
        self.log_text.ensureCursorVisible()
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def check_ffmpeg(self):
        self.log("Checking for FFmpeg installation...")
        
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            self.log(f"✅ FFmpeg found in PATH: {ffmpeg_path}")
            self.status_label.setText("FFmpeg is already installed!")
            self.finish_btn.setVisible(True)
            return
        
        local_ffmpeg = Path(__file__).parent / ".ffmpeg" / "bin" / "ffmpeg.exe"
        if local_ffmpeg.exists():
            self.log(f"✅ FFmpeg found locally: {local_ffmpeg}")
            self.status_label.setText("FFmpeg is already installed!")
            self.finish_btn.setVisible(True)
            return
        
        env_ffmpeg = os.environ.get("FFMPEG_LOCATION")
        if env_ffmpeg and Path(env_ffmpeg).exists():
            self.log(f"✅ FFmpeg found in environment: {env_ffmpeg}")
            self.status_label.setText("FFmpeg is already installed!")
            self.finish_btn.setVisible(True)
            return
        
        self.log("❌ FFmpeg not found")
        self.status_label.setText("FFmpeg is required but not installed")
        
        self.install_btn.setVisible(True)
        self.skip_btn.setVisible(True)
    
    def install_ffmpeg(self):
        self.log("Starting FFmpeg installation...")
        self.status_label.setText("Installing FFmpeg...")
        
        self.install_btn.setEnabled(False)
        self.skip_btn.setEnabled(False)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
                
        install_dir = Path(__file__).parent / ".ffmpeg"
        self.ffmpeg_downloader = FFmpegDownloader(install_dir)
        self.ffmpeg_downloader.progress.connect(self.progress_bar.setValue)
        self.ffmpeg_downloader.status.connect(self.log)
        self.ffmpeg_downloader.finished.connect(self.on_ffmpeg_install_finished)
        self.ffmpeg_downloader.start()
    
    def on_ffmpeg_install_finished(self, success: bool, message: str):
        self.progress_bar.setVisible(False)
        
        if success:
            self.log(f"✅ FFmpeg installed successfully: {message}")
            self.status_label.setText("FFmpeg installed successfully!")
            
            # Set environment variable for the current session
            os.environ["FFMPEG_LOCATION"] = message
            
            self.finish_btn.setVisible(True)
            self.install_btn.setVisible(False)
            self.skip_btn.setVisible(False)
        else:
            self.log(f"❌ FFmpeg installation failed: {message}")
            self.status_label.setText("FFmpeg installation failed")
            
            # Re-enable buttons
            self.install_btn.setEnabled(True)
            self.skip_btn.setEnabled(True)
            
            QMessageBox.critical(self, "Installation Failed", 
                               f"Failed to install FFmpeg:\n{message}\n\nYou can try again or install manually later.")
    
    def skip_ffmpeg(self):
        self.log("User chose to skip FFmpeg installation")
        self.status_label.setText("FFmpeg installation skipped")
        
        # Show warning
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("FFmpeg Required")
        msg.setText("FFmpeg is required for this application to work properly.")
        msg.setInformativeText("You will need to install FFmpeg manually later. You can:\n"
                              "1. Download from https://ffmpeg.org/download.html\n"
                              "2. Run this installer again\n"
                              "3. Place ffmpeg.exe in the same directory as the application")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        
        self.finish_btn.setVisible(True)
        self.install_btn.setVisible(False)
        self.skip_btn.setVisible(False)
    
    def finish_setup(self):
        self.log("Setup completed successfully!")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Setup Complete")
        msg.setText("YouTube Downloader setup is complete!")
        msg.setInformativeText("You can now run the application.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        
        self.close()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YouTube Downloader Installer")
    
    # Set application icon if available
    icon_path = Path(__file__).parent / "svgs" / "logo.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = InstallerWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
