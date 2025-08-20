import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed and return the path to pyinstaller"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Get PyInstaller path
    try:
        import PyInstaller
        pyinstaller_path = os.path.join(os.path.dirname(PyInstaller.__file__), "..", "Scripts", "pyinstaller.exe")
        if os.path.exists(pyinstaller_path):
            return pyinstaller_path
    except:
        pass
    
    # Try to find pyinstaller in PATH or common locations
    pyinstaller_path = shutil.which("pyinstaller")
    if pyinstaller_path:
        return pyinstaller_path
    
    # Try user scripts directory
    user_scripts = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Python", "Python313", "Scripts", "pyinstaller.exe")
    if os.path.exists(user_scripts):
        return user_scripts
    
    # Fallback to module execution
    return [sys.executable, "-m", "PyInstaller"]

def build_installer():
    current_dir = Path(__file__).parent
    installer_file = current_dir / "installer.py"

    dist_dir = current_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Get PyInstaller path
    pyinstaller_path = install_pyinstaller()
    
    cmd = [
        pyinstaller_path,
        "--onefile",
        "--windowed",
        "--name=YouTubeDownloader_Setup",
        f"--icon={current_dir / 'svgs' / 'logo.ico'}",
        f"--add-data={current_dir / 'svgs'};svgs",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtWidgets", 
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=requests",
        "--hidden-import=zipfile",
        str(installer_file)
    ]
    
    print("Building installer...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, cwd=current_dir)
        print(f"\n✅ Installer created successfully!")
        print(f"Location: {dist_dir / 'YouTubeDownloader_Setup.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building installer: {e}")
        return False

def build_app():
 
    current_dir = Path(__file__).parent
    main_file = current_dir / "main.py"

    dist_dir = current_dir / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Get PyInstaller path
    pyinstaller_path = install_pyinstaller()
    
    cmd = [
        pyinstaller_path,
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
        "--hidden-import=json",
        "--hidden-import=zipfile",
        str(main_file)
    ]
    
    print("Building main application...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd, cwd=current_dir)
        print(f"\n✅ Main application created successfully!")
        print(f"Location: {dist_dir / 'YouTubeDownloader.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building main application: {e}")
        return False

def create_package():
    """Create a complete package with both executables"""
    dist_dir = Path(__file__).parent / "dist"

    package_dir = dist_dir / "YouTubeDownloader_Package"
    package_dir.mkdir(exist_ok=True)
    
    installer_exe = dist_dir / "YouTubeDownloader_Setup.exe"
    app_exe = dist_dir / "YouTubeDownloader.exe"
    
    if installer_exe.exists():
        shutil.copy2(installer_exe, package_dir / "YouTubeDownloader_Setup.exe")
        print(f"✅ Copied installer to package")
    
    if app_exe.exists():
        shutil.copy2(app_exe, package_dir / "YouTubeDownloader.exe")
        print(f"✅ Copied main app to package")
    
    readme_content = """# YouTube Downloader Package

This package contains:

1. **YouTubeDownloader_Setup.exe** - Run this first to set up FFmpeg (required dependency)
2. **YouTubeDownloader.exe** - The main application

## Installation Instructions:

1. Run `YouTubeDownloader_Setup.exe` first
2. The installer will check if FFmpeg is installed
3. If FFmpeg is not found, you can choose to install it automatically or skip for later
4. After setup is complete, run `YouTubeDownloader.exe` to use the application

## Manual FFmpeg Installation (if needed):

If you skipped FFmpeg installation, you can install it manually:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the files and place `ffmpeg.exe` in the same directory as `YouTubeDownloader.exe`
3. Or add FFmpeg to your system PATH

## System Requirements:
- Windows 10 or later
- Internet connection (for downloading videos and FFmpeg)
- At least 100MB free disk space

## Support:
If you encounter any issues, please check that FFmpeg is properly installed.
"""
    
    with open(package_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"\n📦 Package created at: {package_dir}")
    return package_dir

def main():
    print("=== YouTube Downloader - Complete Build System ===\n")
    
    # Install PyInstaller if needed
    install_pyinstaller()
    
    success = True
    
    # Build installer
    print("\n1. Building installer...")
    if not build_installer():
        success = False
    
    # Build main application
    print("\n2. Building main application...")
    if not build_app():
        success = False
    
    # Create package
    if success:
        print("\n3. Creating complete package...")
        package_dir = create_package()
        
        print("\n🎉 Build completed successfully!")
        print(f"📁 Package location: {package_dir}")
        print("\nYou can now distribute the entire package folder to users.")
        print("Users should run YouTubeDownloader_Setup.exe first, then YouTubeDownloader.exe")
    else:
        print("\n💥 Build failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
