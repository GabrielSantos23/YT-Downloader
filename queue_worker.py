from __future__ import annotations

from typing import Optional, Dict, Any
from PySide6.QtCore import QThread, Signal
import yt_dlp

from queue_manager import QueueManager, DownloadItem, DownloadStatus


class QueueWorker(QThread):
    progress = Signal(DownloadItem, int, str, str)  # item, percent, speed, eta
    item_started = Signal(DownloadItem)
    item_completed = Signal(DownloadItem, bool, str)  # item, success, message
    queue_finished = Signal()
    
    def __init__(self, queue_manager: QueueManager) -> None:
        super().__init__()
        self.queue_manager = queue_manager
        self._should_stop = False
        self._current_item: Optional[DownloadItem] = None
    
    def stop(self) -> None:
        """Stop the queue processing"""
        self._should_stop = True
    
    def _hook(self, status: Dict[str, Any]) -> None:
        """Progress hook for yt-dlp"""
        if self._current_item and status.get("status") == "downloading":
            try:
                pct = int(float(status.get("_percent_str", "0%").strip().strip("%")))
            except Exception:
                pct = 0
            speed = status.get("_speed_str", "?")
            eta = status.get("_eta_str", "?")
            self.progress.emit(self._current_item, pct, speed, eta)
    
    def run(self) -> None:
        """Process the download queue"""
        while not self._should_stop:
            # Get next pending item
            item = self.queue_manager.get_next_pending()
            if not item:
                break  # No more items to process
            
            self._current_item = item
            
            # Update status to downloading
            self.queue_manager.update_item_status(item, DownloadStatus.DOWNLOADING)
            self.item_started.emit(item)
            
            # Prepare yt-dlp options
            options = {
                **item.options,
                "progress_hooks": [self._hook],
                "quiet": True,
                "noprogress": True,
                "ignoreerrors": False,
            }
            
            try:
                # Download the item
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([item.url])
                
                # Mark as completed
                self.queue_manager.update_item_status(item, DownloadStatus.COMPLETED)
                self.queue_manager.move_to_history(item)
                self.item_completed.emit(item, True, "Download completed successfully")
                
            except Exception as exc:
                error_msg = str(exc)
                # Mark as failed
                self.queue_manager.update_item_status(item, DownloadStatus.FAILED, error_msg)
                self.queue_manager.move_to_history(item)
                self.item_completed.emit(item, False, f"Download failed: {error_msg}")
            
            self._current_item = None
            
            if self._should_stop:
                break
        
        self.queue_finished.emit()

