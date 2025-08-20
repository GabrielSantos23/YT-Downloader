# GitHub Releases & Auto-Update Guide

## 🎉 Complete GitHub Integration

Your YouTube Downloader application now has full GitHub releases integration with automatic update checking! Users will automatically be notified of new versions and can update seamlessly.

## 📋 What's New

### ✅ **Auto-Update System**

- **Background checking** - App checks for updates every 24 hours
- **Smart notifications** - Only shows updates for new versions
- **Skip functionality** - Users can skip specific versions
- **Automatic download** - Downloads and applies updates automatically
- **App restart** - Seamlessly restarts with new version

### ✅ **GitHub Releases Integration**

- **Automated releases** - Create releases with one command
- **Asset upload** - Automatically uploads executables to GitHub
- **Version management** - Tracks and compares versions automatically
- **Release notes** - Include detailed release information

## 🚀 Quick Setup

### Step 1: Configure GitHub Integration

```bash
python setup_github_releases.py
```

This will:

- Ask for your GitHub username and repository name
- Update all files with your repository information
- Show instructions for creating a GitHub token
- Optionally create GitHub Actions workflow

### Step 2: Create GitHub Token

1. Go to GitHub.com → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Set as environment variable: `set GITHUB_TOKEN=your_token`

### Step 3: Test the System

```bash
# Build your application
python build_installer.py

# Create a GitHub release
python create_github_release.py
```

## 📦 Release Process

### Manual Release Creation

```bash
# 1. Build the application
python build_installer.py

# 2. Create GitHub release
python create_github_release.py
```

The script will:

- Ask for version number (e.g., 1.0.1)
- Ask for release notes
- Create GitHub release
- Upload all assets (executables, zip package)
- Update app version automatically

### Automatic Release with GitHub Actions

If you enabled GitHub Actions during setup:

1. **Make your changes** to the code
2. **Build locally** (optional): `python build_installer.py`
3. **Create and push a tag**:
   ```bash
   git add .
   git commit -m "New version"
   git tag v1.0.1
   git push origin v1.0.1
   ```
4. **GitHub Actions automatically**:
   - Builds the application
   - Creates a release
   - Uploads all assets

## 🔄 Auto-Update System

### How It Works

1. **App starts** → Checks for updates after 3 seconds
2. **Background checking** → Checks every 24 hours
3. **Update found** → Shows notification dialog
4. **User chooses** → Update now, remind later, or skip
5. **Download & apply** → Downloads and restarts automatically

### User Experience

- **Seamless updates** - No manual download required
- **Progress tracking** - Shows download progress
- **Error handling** - Graceful fallback if update fails
- **Version skipping** - Remember user preferences

### Update Dialog Options

- **Update Now** - Downloads and applies immediately
- **Remind Me Later** - Shows again next time
- **Skip This Version** - Never shows this version again

## 📁 File Structure

```
ytdownloader/
├── github_release_manager.py    # Core update functionality
├── update_dialog.py             # Update UI and logic
├── create_github_release.py     # Release creation script
├── setup_github_releases.py     # Initial setup script
├── main.py                      # Updated with auto-update
├── config/                      # Configuration files
│   ├── github_config.json       # GitHub repository info
│   └── update_config.json       # User update preferences
└── .github/workflows/           # GitHub Actions (if enabled)
    └── release.yml              # Automatic release workflow
```

## ⚙️ Configuration

### GitHub Configuration

```json
{
  "github_username": "your-username",
  "github_repo": "python-yt-downloader",
  "github_repo_full": "your-username/python-yt-downloader"
}
```

### Update Configuration

```json
{
  "skipped_version": "1.0.1"
}
```

## 🔧 Customization

### Change Update Check Frequency

In `main.py`, modify the timer:

```python
# Check every 12 hours instead of 24
update_timer.start(12 * 60 * 60 * 1000)
```

### Customize Update Dialog

Edit `update_dialog.py` to modify:

- Dialog appearance
- Button text
- Update behavior

### Modify Release Assets

In `create_github_release.py`, change the assets list:

```python
assets_to_upload = [
    package_dir / "YouTubeDownloader_Setup.exe",
    package_dir / "YouTubeDownloader.exe",
    package_dir / "README.txt",
    # Add more files here
]
```

## 🧪 Testing

### Test Auto-Update System

1. **Change version** in `github_release_manager.py`:

   ```python
   CURRENT_VERSION = "0.9.9"  # Lower than release
   ```

2. **Create a release** with higher version:

   ```bash
   python create_github_release.py
   # Enter version: 1.0.0
   ```

3. **Run the app** - Should show update notification

### Test Manual Update

```bash
# Test update checking
python -c "
from github_release_manager import GitHubReleaseManager
manager = GitHubReleaseManager()
print('Update available:', manager.check_for_updates())
"
```

## 🚨 Troubleshooting

### Common Issues

1. **"GitHub token not found"**

   - Create GitHub Personal Access Token
   - Set environment variable: `set GITHUB_TOKEN=your_token`

2. **"Repository not found"**

   - Run `python setup_github_releases.py`
   - Enter correct GitHub username and repository name

3. **"Update check fails"**

   - Check internet connection
   - Verify GitHub repository exists and is public
   - Check if releases exist on GitHub

4. **"Auto-update doesn't work"**
   - Ensure app has write permissions
   - Check if antivirus is blocking the update
   - Verify FFmpeg is properly installed

### Debug Mode

Add debug logging to see what's happening:

```python
# In github_release_manager.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Best Practices

### Release Management

- **Version consistently** - Use semantic versioning (1.0.0, 1.0.1, etc.)
- **Write good release notes** - Explain what's new/fixed
- **Test releases** - Always test before releasing to users
- **Backup before updates** - App creates backups automatically

### User Experience

- **Don't spam updates** - Check frequency is reasonable
- **Clear release notes** - Users should understand changes
- **Graceful fallbacks** - Handle network/update failures
- **Respect user choice** - Remember skipped versions

### Security

- **Use HTTPS** - All downloads are over secure connections
- **Verify downloads** - Consider adding checksums
- **Token security** - Keep GitHub token secure
- **Update validation** - Verify downloaded files

## 🔄 Workflow Examples

### Daily Development

```bash
# 1. Make changes to your code
# 2. Test locally
python main.py

# 3. Build when ready
python build_installer.py

# 4. Test the build
python test_installer.py
```

### Release New Version

```bash
# 1. Build application
python build_installer.py

# 2. Create GitHub release
python create_github_release.py
# Enter version: 1.0.2
# Enter release notes...

# 3. Users get automatic update notifications!
```

### Automatic Release (with GitHub Actions)

```bash
# 1. Make changes and commit
git add .
git commit -m "Add new feature"

# 2. Create and push tag
git tag v1.0.3
git push origin v1.0.3

# 3. GitHub Actions automatically builds and releases!
```

## 🎯 Advanced Features

### Custom Update Channels

You can modify the system to support:

- **Beta releases** - Separate update channel
- **Stable releases** - Main update channel
- **Rolling updates** - Continuous updates

### Update Statistics

Track update adoption:

- Add analytics to update dialog
- Log update attempts
- Monitor success rates

### Delta Updates

For smaller downloads:

- Download only changed files
- Apply patches instead of full replacement
- Reduce bandwidth usage

---

## 🎉 Congratulations!

You now have a professional-grade auto-update system that:

- ✅ Automatically checks for updates
- ✅ Downloads and applies updates seamlessly
- ✅ Integrates with GitHub releases
- ✅ Provides excellent user experience
- ✅ Handles errors gracefully

Your users will always have the latest version without any manual intervention!

**Happy releasing! 🚀**
