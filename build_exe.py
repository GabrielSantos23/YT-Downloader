import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_exe():
    """Build the executable using PyInstaller"""
    current_dir = Path(__file__).parent
    main_file = current_dir / "main.py"
    
    dist_dir = current_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=YouTubeDownloader",
        f"--icon={current_dir / 'svgs' / 'logo.ico'}",
        f"--add-data={current_dir / 'svgs'};svgs",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtWidgets", 
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=yt_dlp",
        "--hidden-import=requests",
        "--hidden-import=PIL",
        str(main_file)
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, cwd=current_dir)
        print(f"\n✅ Executable created successfully!")
        print(f"Location: {dist_dir / 'YouTubeDownloader.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building executable: {e}")
        return False

def main():
    print("=== YouTube Downloader - Executable Builder ===\n")
    
    install_pyinstaller()
    
    if build_exe():
        print("\n🎉 Build completed successfully!")
        print("You can now distribute the YouTubeDownloader.exe file.")
    else:
        print("\n💥 Build failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
