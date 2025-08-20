import os
import sys
import json
import requests
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QMessageBox, QProgressDialog
import subprocess

class GitHubReleaseManager(QObject):
    GITHUB_REPO = "GabrielSantos23/YT-Downloader" 
    GITHUB_API_BASE = "https://api.github.com"
    
    CURRENT_VERSION = "1.0.0"
    
    update_available = Signal(str, str)
    update_progress = Signal(int)
    update_finished = Signal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.latest_release = None
        self.update_download_url = None
    
    def check_for_updates(self) -> bool:
        try:
            url = f"{self.GITHUB_API_BASE}/repos/{self.GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to fetch releases: {response.status_code}")
                return False
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if not latest_version:
                print("No version tag found in latest release")
                return False
            
            if self._compare_versions(latest_version, self.CURRENT_VERSION) > 0:
                assets = release_data.get('assets', [])
                for asset in assets:
                    if asset['name'].endswith('.exe') or asset['name'].endswith('.zip'):
                        self.latest_release = release_data
                        self.update_download_url = asset['browser_download_url']
                        self.update_available.emit(latest_version, asset['browser_download_url'])
                        return True
                
                print("No executable asset found in latest release")
                return False
            
            return False
            
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return False
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if version1 > version2, -1 if version1 < version2, 0 if equal"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            
            return 0
        except:
            return 0
    
    def download_update(self, download_url: str, progress_callback=None) -> bool:
        try:
            temp_dir = Path(__file__).parent / "temp_update"
            temp_dir.mkdir(exist_ok=True)
            
            # Download the file
            response = requests.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded_size = 0
            
            # Determine file extension
            if download_url.endswith('.zip'):
                file_path = temp_dir / "update.zip"
            else:
                file_path = temp_dir / "update.exe"
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if total_size > 0 and progress_callback:
                            progress = int((downloaded_size / total_size) * 100)
                            progress_callback(progress)
            
            if file_path.suffix == '.zip':
                self._extract_update(file_path, temp_dir)
            
            return True
            
        except Exception as e:
            print(f"Error downloading update: {e}")
            return False
    
    def _extract_update(self, zip_path: Path, extract_dir: Path):
        """Extract the update zip file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            print(f"Error extracting update: {e}")
    
    def apply_update(self) -> bool:
        """Apply the downloaded update"""
        try:
            temp_dir = Path(__file__).parent / "temp_update"
            if not temp_dir.exists():
                return False
            
            # Find the new executable
            new_exe = None
            for file in temp_dir.rglob("*.exe"):
                if "YouTubeDownloader" in file.name:
                    new_exe = file
                    break
            
            if not new_exe:
                print("No new executable found in update")
                return False
            
            current_exe = Path(sys.executable)
            if not current_exe.exists():
                current_exe = Path(__file__).parent / "YouTubeDownloader.exe"
            
            backup_path = current_exe.parent / f"{current_exe.stem}_backup.exe"
            shutil.copy2(current_exe, backup_path)
            
            shutil.copy2(new_exe, current_exe)
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return True
            
        except Exception as e:
            print(f"Error applying update: {e}")
            return False


class UpdateCheckerThread(QThread):
    update_found = Signal(str, str)
    check_completed = Signal(bool)
    
    def __init__(self, release_manager: GitHubReleaseManager):
        super().__init__()
        self.release_manager = release_manager
    
    def run(self):
        try:
            has_update = self.release_manager.check_for_updates()
            self.check_completed.emit(True)
            
            if has_update:
                self.update_found.emit(
                    self.release_manager.latest_release['tag_name'],
                    self.release_manager.update_download_url
                )
        except Exception as e:
            print(f"Update check failed: {e}")
            self.check_completed.emit(False)


class UpdateDownloaderThread(QThread):
    progress_updated = Signal(int)
    download_finished = Signal(bool, str)
    
    def __init__(self, release_manager: GitHubReleaseManager, download_url: str):
        super().__init__()
        self.release_manager = release_manager
        self.download_url = download_url
    
    def run(self):
        try:
            success = self.release_manager.download_update(
                self.download_url, 
                self.progress_updated.emit
            )
            
            if success:
                self.download_finished.emit(True, "Download completed successfully")
            else:
                self.download_finished.emit(False, "Download failed")
                
        except Exception as e:
            self.download_finished.emit(False, f"Download error: {str(e)}")


def create_github_release_script():
    script_content = '''#!/usr/bin/env python3


import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def get_github_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        token = input("Enter your GitHub Personal Access Token: ").strip()
    return token

def create_release(version: str, release_notes: str, token: str):
    repo = "GabrielSantos23/YT-Downloader"
    url = f"https://api.github.com/repos/{repo}/releases"
    
    release_data = {
        "tag_name": f"v{version}",
        "name": f"YouTube Downloader v{version}",
        "body": release_notes,
        "draft": False,
        "prerelease": False
    }
    
    # Create release
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post(url, json=release_data, headers=headers)
    
    if response.status_code == 201:
        release_info = response.json()
        print(f"✅ Release created: {release_info['html_url']}")
        return release_info
    else:
        print(f"❌ Failed to create release: {response.status_code}")
        print(response.text)
        return None

def upload_asset(release_id: str, file_path: Path, token: str):
    repo = "GabrielSantos23/YT-Downloader"
    url = f"https://uploads.github.com/repos/{repo}/releases/{release_id}/assets"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    params = {
        "name": file_path.name
    }
    
    with open(file_path, 'rb') as f:
        response = requests.post(url, data=f, headers=headers, params=params)
    
    if response.status_code == 201:
        print(f"✅ Asset uploaded: {file_path.name}")
        return True
    else:
        print(f"❌ Failed to upload {file_path.name}: {response.status_code}")
        return False

def main():
    print("=== GitHub Release Creator ===\\n")
    
    version = input("Enter version (e.g., 1.0.1): ").strip()
    if not version:
        print("❌ Version is required")
        return
    
    print("\\nEnter release notes (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    release_notes = "\\n".join(lines[:-1])  # Remove the last empty line
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        print("❌ GitHub token is required")
        return
    
    dist_dir = Path(__file__).parent / "dist"
    package_dir = dist_dir / "YouTubeDownloader_Package"
    
    if not package_dir.exists():
        print("❌ Distribution package not found. Run build_installer.py first.")
        return
    
    print("\\nCreating GitHub release...")
    release_info = create_release(version, release_notes, token)
    
    if not release_info:
        return
    
    print("\\nUploading assets...")
    assets_to_upload = [
        package_dir / "YouTubeDownloader_Setup.exe",
        package_dir / "YouTubeDownloader.exe",
        package_dir / "README.txt"
    ]
    
    success_count = 0
    for asset in assets_to_upload:
        if asset.exists():
            if upload_asset(release_info['id'], asset, token):
                success_count += 1
        else:
            print(f"⚠️  Asset not found: {asset.name}")
    
    print(f"\\n🎉 Release completed! {success_count}/{len(assets_to_upload)} assets uploaded.")
    print(f"Release URL: {release_info['html_url']}")

if __name__ == "__main__":
    main()
'''
    
    script_path = Path(__file__).parent / "create_github_release.py"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"✅ GitHub release script created: {script_path}")
    return script_path
