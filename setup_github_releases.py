#!/usr/bin/env python3
"""
GitHub Releases Setup Script
This script helps configure your GitHub repository for releases
"""

import os
import sys
import json
from pathlib import Path

def setup_github_config():
    """Setup GitHub configuration"""
    print("=== GitHub Releases Setup ===\n")
    
    # Get GitHub username
    username = input("Enter your GitHub username: ").strip()
    if not username:
        print("❌ GitHub username is required")
        return False
    
    # Get repository name
    repo_name = input("Enter your repository name (default: python-yt-downloader): ").strip()
    if not repo_name:
        repo_name = "python-yt-downloader"
    
    # Create config
    config = {
        "github_username": username,
        "github_repo": repo_name,
        "github_repo_full": f"{username}/{repo_name}"
    }
    
    # Save config
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "github_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ GitHub config saved: {config_file}")
    
    # Update files with the correct repository
    update_files_with_repo(config["github_repo_full"])
    
    return True

def update_files_with_repo(repo_full: str):
    """Update files with the correct repository name"""
    files_to_update = [
        "github_release_manager.py",
        "create_github_release.py"
    ]
    
    for filename in files_to_update:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace placeholder repository
                content = content.replace(
                    "your-username/python-yt-downloader",
                    repo_full
                )
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated {filename}")
                
            except Exception as e:
                print(f"⚠️  Error updating {filename}: {e}")

def create_github_token_instructions():
    """Show instructions for creating GitHub token"""
    print("\n=== GitHub Personal Access Token ===\n")
    print("You need to create a GitHub Personal Access Token to upload releases.")
    print("Follow these steps:")
    print()
    print("1. Go to GitHub.com and sign in")
    print("2. Click your profile picture → Settings")
    print("3. Scroll down to 'Developer settings' (bottom left)")
    print("4. Click 'Personal access tokens' → 'Tokens (classic)'")
    print("5. Click 'Generate new token' → 'Generate new token (classic)'")
    print("6. Give it a name like 'YouTube Downloader Releases'")
    print("7. Select scopes:")
    print("   - ✅ repo (Full control of private repositories)")
    print("8. Click 'Generate token'")
    print("9. Copy the token (you won't see it again!)")
    print()
    print("You can set this token as an environment variable:")
    print("   set GITHUB_TOKEN=your_token_here")
    print()
    print("Or enter it when prompted during release creation.")

def create_workflow_files():
    """Create GitHub Actions workflow files"""
    workflow_dir = Path(__file__).parent.parent / ".github" / "workflows"
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    # Create release workflow
    workflow_content = '''name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r ytdownloader/requirements.txt
    
    - name: Build application
      run: |
        cd ytdownloader
        python build_installer.py
    
    - name: Create Release
      uses: softprops/action-gh-release@v1
      with:
        files: |
          ytdownloader/dist/YouTubeDownloader_Package.zip
          ytdownloader/dist/YouTubeDownloader_Setup.exe
          ytdownloader/dist/YouTubeDownloader.exe
          ytdownloader/dist/YouTubeDownloader_Package/README.txt
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    
    workflow_file = workflow_dir / "release.yml"
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    print(f"✅ Created GitHub Actions workflow: {workflow_file}")

def main():
    """Main setup function"""
    print("YouTube Downloader - GitHub Releases Setup\n")
    print("This script will help you configure GitHub releases for your application.\n")
    
    # Setup GitHub config
    if not setup_github_config():
        return
    
    # Show token instructions
    create_github_token_instructions()
    
    # Create workflow files
    print("\n=== GitHub Actions Workflow ===\n")
    create_workflow = input("Create GitHub Actions workflow for automatic releases? (y/n): ").strip().lower()
    if create_workflow == 'y':
        create_workflow_files()
        print("\n✅ GitHub Actions workflow created!")
        print("Now you can create releases by:")
        print("1. Making changes to your code")
        print("2. Running: python build_installer.py")
        print("3. Creating a git tag: git tag v1.0.1")
        print("4. Pushing the tag: git push origin v1.0.1")
        print("5. GitHub Actions will automatically build and release!")
    
    print("\n=== Setup Complete! ===\n")
    print("Next steps:")
    print("1. Create a GitHub Personal Access Token")
    print("2. Test the release process:")
    print("   python build_installer.py")
    print("   python create_github_release.py")
    print("3. Users will automatically get update notifications!")

if __name__ == "__main__":
    main()
