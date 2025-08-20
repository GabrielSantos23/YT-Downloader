from __future__ import annotations

import os
import sys
import shutil
import zipfile
from pathlib import Path
from typing import Optional

import requests
from PySide6.QtCore import QThread, Signal


FFMPEG_WIN_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip"


def default_install_dir() -> Path:
    base = Path(__file__).resolve().parent
    return base / ".ffmpeg"


def find_ffmpeg_dir() -> Optional[str]:
    # Env override
    env = os.environ.get("FFMPEG_LOCATION")
    if env and os.path.exists(env):
        return env
    # PATH
    exe = shutil.which("ffmpeg")
    if exe:
        return str(Path(exe).parent)
    # App local
    local_bin = default_install_dir() / "bin"
    if local_bin.exists():
        return str(local_bin)
    return None


class FFmpegInstallWorker(QThread):
    progress = Signal(int)
    done = Signal(bool, str, str)  # ok, message, ffmpeg_dir

    def __init__(self, target_dir: Optional[Path] = None) -> None:
        super().__init__()
        self.target_dir = target_dir or default_install_dir()

    def run(self) -> None:
        try:
            self.target_dir.mkdir(parents=True, exist_ok=True)
            url = self._pick_url()
            zip_path = self.target_dir / "ffmpeg.zip"
            self._download(url, zip_path)
            bin_dir = self._extract_find_bin(zip_path)
            if not bin_dir or not (Path(bin_dir) / ("ffmpeg.exe" if sys.platform.startswith("win") else "ffmpeg")).exists():
                raise RuntimeError("FFmpeg binary not found after extraction")
            self.done.emit(True, "FFmpeg installed", str(bin_dir))
        except Exception as exc:
            self.done.emit(False, str(exc), "")

    def _pick_url(self) -> str:
        if sys.platform.startswith("win"):
            return FFMPEG_WIN_URL
        # Fallback: advise user (non-Windows)
        raise RuntimeError("Auto-install currently supported on Windows only. Please install FFmpeg via your package manager.")

    def _download(self, url: str, dest: Path) -> None:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            written = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    f.write(chunk)
                    written += len(chunk)
                    if total:
                        self.progress.emit(int(written * 100 / total))

    def _extract_find_bin(self, archive_path: Path) -> Optional[str]:
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(self.target_dir)
        # Search for bin directory that contains ffmpeg(.exe)
        for root, dirs, files in os.walk(self.target_dir):
            if ("ffmpeg.exe" in files) or ("ffmpeg" in files):
                return root
        return None









