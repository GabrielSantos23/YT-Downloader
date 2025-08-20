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
        
        self.history_file = self.data_dir / "history.json"
        
        self.history: List[DownloadItem] = []
        
        self._load_data()
    
    def _load_data(self) -> None:
        """Load history from disk"""
        # Load history
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [DownloadItem.from_dict(item) for item in data]
            except Exception:
                self.history = []
    

    
    def _save_history(self) -> None:
        """Save history to disk"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([item.to_dict() for item in self.history], f, indent=2)
        except Exception:
            pass  # Silently fail if we can't save
    
    def add_to_history(self, item: DownloadItem) -> None:
        """Add a new download directly to history"""
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
        """Create a new history item from a failed download"""
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
        self.add_to_history(new_item)
        return new_item

