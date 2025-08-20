#!/usr/bin/env python3
"""
GitHub Release Automation Script
This script helps create GitHub releases with the built executables
"""

import os
import sys
import subprocess
import requests
import json
from pathlib import Path

def get_github_token():
    """Get GitHub token from environment or prompt user"""
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        token = input("Enter your GitHub Personal Access Token: ").strip()
    return token

def create_release(version: str, release_notes: str, token: str):
    """Create a GitHub release"""
    # GitHub API endpoint
    repo = "GabrielSantos23/YT-Downloader"  # Update with your repo
    url = f"https://api.github.com/repos/{repo}/releases"
    
    # Release data
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
    """Upload asset to GitHub release"""
    repo = "GabrielSantos23/YT-Downloader"  # Update with your repo
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

def create_zip_package():
    """Create a zip package of the distribution"""
    dist_dir = Path(__file__).parent / "dist"
    package_dir = dist_dir / "YouTubeDownloader_Package"
    
    if not package_dir.exists():
        print("❌ Distribution package not found. Run build_installer.py first.")
        return None
    
    # Create zip file
    import zipfile
    zip_path = dist_dir / "YouTubeDownloader_Package.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Zip package created: {zip_path}")
    return zip_path

def main():
    """Main function"""
    print("=== GitHub Release Creator ===\n")
    
    # Get version
    version = input("Enter version (e.g., 1.0.1): ").strip()
    if not version:
        print("❌ Version is required")
        return
    
    # Get release notes
    print("\nEnter release notes (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    release_notes = "\n".join(lines[:-1])  # Remove the last empty line
    
    # Get GitHub token
    token = get_github_token()
    if not token:
        print("❌ GitHub token is required")
        return
    
    # Check if executables exist
    dist_dir = Path(__file__).parent / "dist"
    package_dir = dist_dir / "YouTubeDownloader_Package"
    
    if not package_dir.exists():
        print("❌ Distribution package not found. Run build_installer.py first.")
        return
    
    # Create release
    print("\nCreating GitHub release...")
    release_info = create_release(version, release_notes, token)
    
    if not release_info:
        return
    
    # Create zip package
    print("\nCreating zip package...")
    zip_path = create_zip_package()
    
    # Upload assets
    print("\nUploading assets...")
    assets_to_upload = [
        package_dir / "YouTubeDownloader_Setup.exe",
        package_dir / "YouTubeDownloader.exe",
        package_dir / "README.txt"
    ]
    
    if zip_path:
        assets_to_upload.append(zip_path)
    
    success_count = 0
    for asset in assets_to_upload:
        if asset.exists():
            if upload_asset(release_info['id'], asset, token):
                success_count += 1
        else:
            print(f"⚠️  Asset not found: {asset.name}")
    
    print(f"\n🎉 Release completed! {success_count}/{len(assets_to_upload)} assets uploaded.")
    print(f"Release URL: {release_info['html_url']}")
    
    # Update version in the app
    update_app_version(version)

def update_app_version(version: str):
    """Update the version in the GitHub release manager"""
    try:
        release_manager_path = Path(__file__).parent / "github_release_manager.py"
        
        if release_manager_path.exists():
            with open(release_manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update the version
            import re
            content = re.sub(
                r'CURRENT_VERSION = "[^"]*"',
                f'CURRENT_VERSION = "{version}"',
                content
            )
            
            with open(release_manager_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated app version to {version}")
        else:
            print("⚠️  Could not find github_release_manager.py to update version")
            
    except Exception as e:
        print(f"⚠️  Error updating app version: {e}")

if __name__ == "__main__":
    main()
