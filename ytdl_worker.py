from __future__ import annotations

from typing import Dict, Any, List, Optional

from PySide6.QtCore import QThread, Signal
import yt_dlp
import requests
import subprocess
import sys


def probe_url_metadata(url: str) -> Optional[Dict[str, Any]]:
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            return ydl.extract_info(url, download=False)
    except Exception:
        return None


def list_formats(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for f in info.get("formats", []) or []:
        result.append(
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "width": f.get("width"),
                "height": f.get("height"),
                "resolution": f.get("resolution") or f"{f.get('width','?')}x{f.get('height','?')}",
                "fps": f.get("fps"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "abr": f.get("abr"),
                "filesize": f.get("filesize"),
                "filesize_approx": f.get("filesize_approx"),
                "format_note": f.get("format_note"),
            }
        )
    return result


class YtDlWorker(QThread):
    progress = Signal(int, str, str)
    error = Signal(str)
    done = Signal(bool, str)

    def __init__(self, url: str, ydl_opts: Dict[str, Any]) -> None:
        super().__init__()
        self.url = url
        self.ydl_opts = {**ydl_opts}

    def _hook(self, status: Dict[str, Any]) -> None:
        if status.get("status") == "downloading":
            try:
                pct = int(float(status.get("_percent_str", "0%").strip().strip("%")))
            except Exception:
                pct = 0
            speed = status.get("_speed_str", "?")
            eta = status.get("_eta_str", "?")
            self.progress.emit(pct, speed, eta)

    def run(self) -> None:
        options = {
            **self.ydl_opts,
            "progress_hooks": [self._hook],
            "quiet": True,
            "noprogress": True,
            "ignoreerrors": False,
        }
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])
            self.done.emit(True, "Download complete.")
        except Exception as exc:
            self.error.emit(str(exc))
            self.done.emit(False, "Download failed.")


class InfoWorker(QThread):
    info = Signal(dict)
    error = Signal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url

    def run(self) -> None:
        try:
            info = probe_url_metadata(self.url) or {}
            if not info:
                raise RuntimeError("Failed to extract video info")
            self.info.emit(info)
        except Exception as exc:
            self.error.emit(str(exc))


class ThumbWorker(QThread):
    ready = Signal(bytes)
    error = Signal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url

    def run(self) -> None:
        try:
            resp = requests.get(self.url, timeout=10)
            resp.raise_for_status()
            self.ready.emit(resp.content)
        except Exception as exc:
            self.error.emit(str(exc))


class PipUpdateWorker(QThread):
    progress = Signal(str)
    done = Signal(bool, str)

    def run(self) -> None:
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            assert process.stdout is not None
            for line in process.stdout:
                self.progress.emit(line.rstrip())
            rc = process.wait()
            if rc == 0:
                self.done.emit(True, "yt-dlp updated successfully")
            else:
                self.done.emit(False, f"pip exited with code {rc}")
        except Exception as exc:
            self.done.emit(False, str(exc))


