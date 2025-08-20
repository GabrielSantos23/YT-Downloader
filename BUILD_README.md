# YouTube Downloader - Build and Distribution Guide

This guide explains how to create executable files (.exe) for your YouTube Downloader application and distribute it to users.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **All dependencies** installed (run `pip install -r requirements.txt`)
3. **Windows OS** (for creating Windows executables)

## Quick Start

### Option 1: Use the Batch File (Recommended)

1. Double-click `build.bat` in the project directory
2. Wait for the build process to complete
3. Check the `dist` folder for your executables

### Option 2: Manual Build

1. Open a command prompt in the project directory
2. Run: `python build_installer.py`
3. Check the `dist` folder for your executables

## What Gets Created

After running the build script, you'll find:

### In the `dist` folder:

- `YouTubeDownloader.exe` - The main application
- `YouTubeDownloader_Setup.exe` - The installer that checks for FFmpeg
- `YouTubeDownloader_Package/` - Complete distribution package containing:
  - `YouTubeDownloader_Setup.exe`
  - `YouTubeDownloader.exe`
  - `README.txt` - Instructions for users

## Distribution Package

The `YouTubeDownloader_Package` folder contains everything needed to distribute your application:

### Files Included:

1. **YouTubeDownloader_Setup.exe** - First file users should run
2. **YouTubeDownloader.exe** - The main application
3. **README.txt** - User instructions

### User Installation Process:

1. User downloads and extracts the package
2. User runs `YouTubeDownloader_Setup.exe`
3. Installer checks for FFmpeg:
   - If found: Setup completes
   - If not found: User can choose to install FFmpeg automatically or skip
4. User runs `YouTubeDownloader.exe` to use the application

## FFmpeg Integration

The installer automatically handles FFmpeg dependency:

### What the Installer Does:

1. **Checks for FFmpeg** in multiple locations:

   - System PATH
   - Local `.ffmpeg` directory
   - Environment variable `FFMPEG_LOCATION`

2. **If FFmpeg is missing**:

   - Offers to download and install automatically
   - Downloads from official FFmpeg builds
   - Installs to local `.ffmpeg` directory
   - Sets up environment variables

3. **If user skips installation**:
   - Shows clear instructions for manual installation
   - Explains why FFmpeg is required
   - Provides alternative installation methods

### FFmpeg Installation Locations:

- **Automatic**: `./.ffmpeg/bin/ffmpeg.exe` (relative to app directory)
- **Manual**: User can place `ffmpeg.exe` in the same directory as the app
- **System**: User can add FFmpeg to system PATH

## Build Scripts Explained

### `build_exe.py`

- Creates only the main application executable
- Use this if you only need the app without the installer

### `build_installer.py`

- Creates both the installer and main application
- Creates a complete distribution package
- Recommended for full distribution

### `installer.py`

- The installer application source code
- Handles FFmpeg detection and installation
- Provides user-friendly setup interface

## Customization

### Changing Application Name:

Edit the `--name` parameter in the build scripts:

```python
"--name=YourAppName"
```

### Changing Icons:

Replace the icon file at `svgs/logo.ico` with your own icon.

### Adding Additional Files:

Add `--add-data` parameters to include additional files:

```python
f"--add-data={path_to_file};destination_folder"
```

## Troubleshooting

### Common Issues:

1. **"PyInstaller not found"**

   - Run: `pip install pyinstaller`

2. **"Missing dependencies"**

   - Run: `pip install -r requirements.txt`

3. **"Executable too large"**

   - Consider using `--onedir` instead of `--onefile`
   - Remove unnecessary hidden imports

4. **"FFmpeg not found after installation"**
   - Check that the download URL is still valid
   - Verify internet connection during installation

### Build Optimization:

1. **Reduce executable size**:

   ```python
   # Use --onedir instead of --onefile
   "--onedir"
   ```

2. **Exclude unnecessary modules**:

   ```python
   "--exclude-module=unnecessary_module"
   ```

3. **Optimize imports**:
   - Only include necessary `--hidden-import` statements

## Distribution Tips

1. **Test thoroughly** on a clean Windows machine
2. **Include clear instructions** in the README.txt
3. **Consider antivirus false positives** - you may need to sign your executables
4. **Provide support contact** information
5. **Version your releases** clearly

## Advanced Features

### Creating Different Builds:

- **Debug build**: Remove `--windowed` flag to show console
- **Portable build**: Use `--onedir` for easier updates
- **Installer build**: Use `--onefile` for single executable

### Code Signing (Optional):

For professional distribution, consider code signing your executables to avoid antivirus warnings.

## Support

If you encounter build issues:

1. Check that all dependencies are installed
2. Verify Python version compatibility
3. Ensure sufficient disk space for build process
4. Check Windows Defender/antivirus isn't blocking the build

---

**Note**: This build system is designed for Windows. For other platforms, you'll need to modify the build scripts and FFmpeg download URLs accordingly.
