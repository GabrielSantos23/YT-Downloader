from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QProgressBar,
    QMessageBox,
    QHeaderView,
    QMenu,
    QAbstractItemView,
    QWidget,
)
from PySide6.QtGui import QAction

from queue_manager import QueueManager, DownloadItem, DownloadStatus


class QueueDialog(QDialog):
    item_selected = Signal(DownloadItem)
    
    def __init__(self, queue_manager: QueueManager, parent=None):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.setWindowTitle("Download Queue")
        self.setMinimumSize(800, 500)
        
        self.setup_ui()
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_table)
        self.refresh_timer.start(1000)  # Refresh every second
        
        self.refresh_table()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self.status_label = QLabel("Queue: 0 items")
        header.addWidget(self.status_label)
        header.addStretch(1)
        
        # Control buttons
        self.start_btn = QPushButton("Start Queue")
        self.pause_btn = QPushButton("Pause")
        self.clear_btn = QPushButton("Clear Completed")
        self.retry_failed_btn = QPushButton("Retry Failed")
        
        header.addWidget(self.start_btn)
        header.addWidget(self.pause_btn)
        header.addWidget(self.clear_btn)
        header.addWidget(self.retry_failed_btn)
        layout.addLayout(header)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Title", "Channel", "Status", "Progress", "Added", "Format", "Actions"
        ])
        
        # Set column widths
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)  # Title
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Channel
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Progress
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Added
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Format
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
        # Connect signals
        self.start_btn.clicked.connect(self.start_queue)
        self.pause_btn.clicked.connect(self.pause_queue)
        self.clear_btn.clicked.connect(self.clear_completed)
        self.retry_failed_btn.clicked.connect(self.retry_failed)
        
        # Initial button states
        self.pause_btn.setEnabled(False)
    
    def refresh_table(self):
        """Refresh the queue table"""
        items = self.queue_manager.get_queue()
        self.table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # Title
            title_item = QTableWidgetItem(item.title[:50] + "..." if len(item.title) > 50 else item.title)
            title_item.setData(Qt.UserRole, item)
            self.table.setItem(row, 0, title_item)
            
            # Channel
            self.table.setItem(row, 1, QTableWidgetItem(item.uploader))
            
            # Status
            status_item = QTableWidgetItem(item.status.value.title())
            if item.status == DownloadStatus.COMPLETED:
                status_item.setBackground(Qt.green)
            elif item.status == DownloadStatus.FAILED:
                status_item.setBackground(Qt.red)
            elif item.status == DownloadStatus.DOWNLOADING:
                status_item.setBackground(Qt.blue)
            self.table.setItem(row, 2, status_item)
            
            # Progress
            if item.status == DownloadStatus.DOWNLOADING:
                progress = QProgressBar()
                progress.setRange(0, 100)
                progress.setValue(0)  # TODO: Get actual progress
                self.table.setCellWidget(row, 3, progress)
            else:
                self.table.setItem(row, 3, QTableWidgetItem(""))
            
            # Added date
            added_str = item.added_at.strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row, 4, QTableWidgetItem(added_str))
            
            # Format
            format_str = item.selected_format or "Auto"
            self.table.setItem(row, 5, QTableWidgetItem(format_str))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            if item.status == DownloadStatus.PENDING:
                remove_btn = QPushButton("Remove")
                remove_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
                actions_layout.addWidget(remove_btn)
            elif item.status == DownloadStatus.FAILED:
                retry_btn = QPushButton("Retry")
                retry_btn.clicked.connect(lambda checked, r=row: self.retry_item(r))
                actions_layout.addWidget(retry_btn)
            
            actions_layout.addStretch()
            self.table.setCellWidget(row, 6, actions_widget)
        
        # Update status label
        pending_count = len([item for item in items if item.status == DownloadStatus.PENDING])
        downloading_count = len([item for item in items if item.status == DownloadStatus.DOWNLOADING])
        completed_count = len([item for item in items if item.status == DownloadStatus.COMPLETED])
        failed_count = len([item for item in items if item.status == DownloadStatus.FAILED])
        
        status_text = f"Queue: {len(items)} items (Pending: {pending_count}, Downloading: {downloading_count}, Completed: {completed_count}, Failed: {failed_count})"
        self.status_label.setText(status_text)
    
    def show_context_menu(self, position):
        """Show context menu for table items"""
        item = self.table.itemAt(position)
        if not item:
            return
        
        download_item = item.data(Qt.UserRole)
        if not download_item:
            return
        
        menu = QMenu(self)
        
        # Add actions based on status
        if download_item.status == DownloadStatus.PENDING:
            remove_action = QAction("Remove from Queue", self)
            remove_action.triggered.connect(lambda: self.remove_item_by_item(download_item))
            menu.addAction(remove_action)
        
        elif download_item.status == DownloadStatus.FAILED:
            retry_action = QAction("Retry Download", self)
            retry_action.triggered.connect(lambda: self.retry_item_by_item(download_item))
            menu.addAction(retry_action)
        
        # Common actions
        copy_url_action = QAction("Copy URL", self)
        copy_url_action.triggered.connect(lambda: self.copy_url(download_item.url))
        menu.addAction(copy_url_action)
        
        open_folder_action = QAction("Open Output Folder", self)
        open_folder_action.triggered.connect(lambda: self.open_output_folder(download_item.output_path))
        menu.addAction(open_folder_action)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def remove_item(self, row: int):
        """Remove item from queue by row index"""
        try:
            self.queue_manager.remove_from_queue(row)
            self.refresh_table()
        except IndexError:
            pass
    
    def remove_item_by_item(self, item: DownloadItem):
        """Remove specific item from queue"""
        if item in self.queue_manager.queue:
            self.queue_manager.queue.remove(item)
            self.queue_manager._save_queue()
            self.refresh_table()
    
    def retry_item(self, row: int):
        """Retry failed item by row index"""
        items = self.queue_manager.get_queue()
        if 0 <= row < len(items):
            item = items[row]
            if item.status == DownloadStatus.FAILED:
                self.retry_item_by_item(item)
    
    def retry_item_by_item(self, item: DownloadItem):
        """Retry specific failed item"""
        if item.status == DownloadStatus.FAILED:
            new_item = self.queue_manager.retry_failed_download(item)
            self.refresh_table()
    
    def start_queue(self):
        """Start processing the queue"""
        # This will be handled by the main window
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
    
    def pause_queue(self):
        """Pause queue processing"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
    
    def clear_completed(self):
        """Clear completed items from queue"""
        reply = QMessageBox.question(
            self, "Clear Completed", 
            "Remove all completed downloads from the queue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Move completed items to history
            items = self.queue_manager.get_queue()
            for item in items:
                if item.status == DownloadStatus.COMPLETED:
                    self.queue_manager.move_to_history(item)
            self.refresh_table()
    
    def retry_failed(self):
        """Retry all failed downloads"""
        failed_items = self.queue_manager.get_failed_downloads()
        if not failed_items:
            QMessageBox.information(self, "No Failed Downloads", "No failed downloads to retry.")
            return
        
        reply = QMessageBox.question(
            self, "Retry Failed", 
            f"Retry {len(failed_items)} failed downloads?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in failed_items:
                self.queue_manager.retry_failed_download(item)
            self.refresh_table()
    
    def copy_url(self, url: str):
        """Copy URL to clipboard"""
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(url)
    
    def open_output_folder(self, output_path: str):
        """Open the output folder in file explorer"""
        import os
        import subprocess
        import platform
        
        folder_path = os.path.dirname(output_path)
        if os.path.exists(folder_path):
            if platform.system() == "Windows":
                subprocess.run(["explorer", folder_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
    
    def closeEvent(self, event):
        """Clean up when dialog is closed"""
        self.refresh_timer.stop()
        super().closeEvent(event)
