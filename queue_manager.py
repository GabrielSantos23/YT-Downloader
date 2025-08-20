from __future__ import annotations

import json
import os
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path


class DownloadStatus(Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadItem:
    url: str
    title: str
    uploader: str
    duration: Optional[int]
    thumbnail_url: Optional[str]
    selected_format: Optional[str]
    output_path: str
    options: Dict[str, Any]  # ydl_opts
    status: DownloadStatus
    added_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None
    download_speed: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['added_at'] = self.added_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DownloadItem:
        data = data.copy()
        data['status'] = DownloadStatus(data['status'])
        data['added_at'] = datetime.fromisoformat(data['added_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class QueueManager:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.ytdownloader")
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.queue_file = self.data_dir / "queue.json"
        self.history_file = self.data_dir / "history.json"
        
        self.queue: List[DownloadItem] = []
        self.history: List[DownloadItem] = []
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load queue and history from disk"""
        # Load queue
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.queue = [DownloadItem.from_dict(item) for item in data]
            except Exception:
                self.queue = []
        
        # Load history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [DownloadItem.from_dict(item) for item in data]
            except Exception:
                self.history = []
    
    def _save_queue(self) -> None:
        """Save queue to disk"""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump([item.to_dict() for item in self.queue], f, indent=2)
        except Exception:
            pass  # Silently fail if we can't save
    
    def _save_history(self) -> None:
        """Save history to disk"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([item.to_dict() for item in self.history], f, indent=2)
        except Exception:
            pass  # Silently fail if we can't save
    
    def add_to_queue(self, item: DownloadItem) -> None:
        """Add a new download to the queue"""
        self.queue.append(item)
        self._save_queue()
    
    def remove_from_queue(self, index: int) -> DownloadItem:
        """Remove item from queue by index"""
        if 0 <= index < len(self.queue):
            item = self.queue.pop(index)
            self._save_queue()
            return item
        raise IndexError("Invalid queue index")
    
    def get_queue(self) -> List[DownloadItem]:
        """Get all items in queue"""
        return self.queue.copy()
    
    def get_pending_items(self) -> List[DownloadItem]:
        """Get items that are pending download"""
        return [item for item in self.queue if item.status == DownloadStatus.PENDING]
    
    def get_next_pending(self) -> Optional[DownloadItem]:
        """Get the next pending item"""
        pending = self.get_pending_items()
        return pending[0] if pending else None
    
    def update_item_status(self, item: DownloadItem, status: DownloadStatus, 
                          error_message: Optional[str] = None) -> None:
        """Update the status of a queue item"""
        item.status = status
        
        if status == DownloadStatus.DOWNLOADING and not item.started_at:
            item.started_at = datetime.now()
        elif status in (DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED):
            item.completed_at = datetime.now()
            if error_message:
                item.error_message = error_message
        
        self._save_queue()
    
    def move_to_history(self, item: DownloadItem) -> None:
        """Move completed/failed item to history"""
        if item in self.queue:
            self.queue.remove(item)
            self._save_queue()
        
        # Keep only last 100 items in history
        self.history.append(item)
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self._save_history()
    
    def clear_completed_history(self) -> None:
        """Clear completed items from history"""
        self.history = [item for item in self.history if item.status == DownloadStatus.FAILED]
        self._save_history()
    
    def clear_all_history(self) -> None:
        """Clear all history"""
        self.history.clear()
        self._save_history()
    
    def get_history(self) -> List[DownloadItem]:
        """Get all history items"""
        return self.history.copy()
    
    def get_failed_downloads(self) -> List[DownloadItem]:
        """Get failed downloads from history"""
        return [item for item in self.history if item.status == DownloadStatus.FAILED]
    
    def retry_failed_download(self, item: DownloadItem) -> DownloadItem:
        """Create a new queue item from a failed download"""
        new_item = DownloadItem(
            url=item.url,
            title=item.title,
            uploader=item.uploader,
            duration=item.duration,
            thumbnail_url=item.thumbnail_url,
            selected_format=item.selected_format,
            output_path=item.output_path,
            options=item.options,
            status=DownloadStatus.PENDING,
            added_at=datetime.now()
        )
        self.add_to_queue(new_item)
        return new_item

