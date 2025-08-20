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
    QMessageBox,
    QHeaderView,
    QMenu,
    QAbstractItemView,
    QComboBox,
    QLineEdit,
    QWidget,
)
from PySide6.QtGui import QAction

from queue_manager import QueueManager, DownloadItem, DownloadStatus


class HistoryDialog(QDialog):
    item_selected = Signal(DownloadItem)
    redownload_requested = Signal(DownloadItem)
    
    def __init__(self, queue_manager: QueueManager, parent=None):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.setWindowTitle("Download History")
        self.setMinimumSize(900, 600)
        
        self.setup_ui()
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_table)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        self.refresh_table()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with filters
        header = QHBoxLayout()
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "Failed", "Cancelled"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        header.addWidget(QLabel("Status:"))
        header.addWidget(self.status_filter)
        
        # Search filter
        self.search_filter = QLineEdit()
        self.search_filter.setPlaceholderText("Search titles, channels...")
        self.search_filter.textChanged.connect(self.apply_filters)
        header.addWidget(QLabel("Search:"))
        header.addWidget(self.search_filter, 1)
        
        # Control buttons
        self.retry_failed_btn = QPushButton("Retry All Failed")
        self.clear_completed_btn = QPushButton("Clear Completed")
        self.clear_all_btn = QPushButton("Clear All")
        self.export_btn = QPushButton("Export")
        
        header.addWidget(self.retry_failed_btn)
        header.addWidget(self.clear_completed_btn)
        header.addWidget(self.clear_all_btn)
        header.addWidget(self.export_btn)
        
        layout.addLayout(header)
        
        # Status label
        self.status_label = QLabel("History: 0 items")
        layout.addWidget(self.status_label)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Title", "Channel", "Status", "Added", "Completed", "Duration", "Format", "Actions"
        ])
        
        # Set column widths
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)  # Title
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Channel
        header_view.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Status
        header_view.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Added
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Completed
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Duration
        header_view.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Format
        header_view.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Actions
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.table)
        
        # Connect signals
        self.retry_failed_btn.clicked.connect(self.retry_all_failed)
        self.clear_completed_btn.clicked.connect(self.clear_completed)
        self.clear_all_btn.clicked.connect(self.clear_all)
        self.export_btn.clicked.connect(self.export_history)
    
    def apply_filters(self):
        """Apply status and search filters"""
        self.refresh_table()
    
    def refresh_table(self):
        """Refresh the history table"""
        items = self.queue_manager.get_history()
        
        # Apply filters
        status_filter = self.status_filter.currentText()
        search_text = self.search_filter.text().lower()
        
        filtered_items = []
        for item in items:
            # Status filter
            if status_filter != "All" and item.status.value.title() != status_filter:
                continue
            
            # Search filter
            if search_text:
                if (search_text not in item.title.lower() and 
                    search_text not in item.uploader.lower()):
                    continue
            
            filtered_items.append(item)
        
        self.table.setRowCount(len(filtered_items))
        
        for row, item in enumerate(filtered_items):
            # Title
            title_item = QTableWidgetItem(item.title[:60] + "..." if len(item.title) > 60 else item.title)
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
            elif item.status == DownloadStatus.CANCELLED:
                status_item.setBackground(Qt.yellow)
            self.table.setItem(row, 2, status_item)
            
            # Added date
            added_str = item.added_at.strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row, 3, QTableWidgetItem(added_str))
            
            # Completed date
            if item.completed_at:
                completed_str = item.completed_at.strftime("%Y-%m-%d %H:%M")
            else:
                completed_str = "-"
            self.table.setItem(row, 4, QTableWidgetItem(completed_str))
            
            # Duration
            if item.duration:
                mins = int(item.duration // 60)
                secs = int(item.duration % 60)
                duration_str = f"{mins}m {secs}s"
            else:
                duration_str = "-"
            self.table.setItem(row, 5, QTableWidgetItem(duration_str))
            
            # Format
            format_str = item.selected_format or "Auto"
            self.table.setItem(row, 6, QTableWidgetItem(format_str))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            # Add re-download button for all items
            redownload_btn = QPushButton("Re-download")
            redownload_btn.clicked.connect(lambda checked, r=row: self.redownload_item(r))
            actions_layout.addWidget(redownload_btn)
            
            if item.status == DownloadStatus.FAILED:
                retry_btn = QPushButton("Retry")
                retry_btn.clicked.connect(lambda checked, r=row: self.retry_item(r))
                actions_layout.addWidget(retry_btn)
            
            actions_layout.addStretch()
            self.table.setCellWidget(row, 7, actions_widget)
        
        # Update status label
        total_count = len(items)
        completed_count = len([item for item in items if item.status == DownloadStatus.COMPLETED])
        failed_count = len([item for item in items if item.status == DownloadStatus.FAILED])
        cancelled_count = len([item for item in items if item.status == DownloadStatus.CANCELLED])
        
        status_text = f"History: {total_count} items (Completed: {completed_count}, Failed: {failed_count}, Cancelled: {cancelled_count})"
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
        
        # Add re-download action for all items
        redownload_action = QAction("Re-download", self)
        redownload_action.triggered.connect(lambda: self.redownload_item_by_item(download_item))
        menu.addAction(redownload_action)
        
        # Add actions based on status
        if download_item.status == DownloadStatus.FAILED:
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
        
        if download_item.error_message:
            show_error_action = QAction("Show Error", self)
            show_error_action.triggered.connect(lambda: self.show_error(download_item.error_message))
            menu.addAction(show_error_action)
        
        menu.exec(self.table.mapToGlobal(position))
    
    def retry_item(self, row: int):
        """Retry failed item by row index"""
        items = self.queue_manager.get_history()
        if 0 <= row < len(items):
            item = items[row]
            if item.status == DownloadStatus.FAILED:
                self.retry_item_by_item(item)
    
    def redownload_item(self, row: int):
        """Re-download item by row index"""
        items = self.queue_manager.get_history()
        if 0 <= row < len(items):
            item = items[row]
            self.redownload_item_by_item(item)
    
    def redownload_item_by_item(self, item: DownloadItem):
        """Re-download specific item"""
        self.redownload_requested.emit(item)
        self.close()
    
    def retry_item_by_item(self, item: DownloadItem):
        """Retry specific failed item"""
        if item.status == DownloadStatus.FAILED:
            new_item = self.queue_manager.retry_failed_download(item)
            self.refresh_table()
    
    def retry_all_failed(self):
        """Retry all failed downloads"""
        failed_items = self.queue_manager.get_failed_downloads()
        if not failed_items:
            QMessageBox.information(self, "No Failed Downloads", "No failed downloads to retry.")
            return
        
        reply = QMessageBox.question(
            self, "Retry All Failed", 
            f"Retry {len(failed_items)} failed downloads?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in failed_items:
                self.queue_manager.retry_failed_download(item)
            self.refresh_table()
    
    def clear_completed(self):
        """Clear completed items from history"""
        reply = QMessageBox.question(
            self, "Clear Completed", 
            "Remove all completed downloads from history?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.queue_manager.clear_completed_history()
            self.refresh_table()
    
    def clear_all(self):
        """Clear all history"""
        reply = QMessageBox.question(
            self, "Clear All History", 
            "Remove all downloads from history? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.queue_manager.clear_all_history()
            self.refresh_table()
    
    def export_history(self):
        """Export history to CSV"""
        import csv
        import os
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export History", "download_history.csv", "CSV Files (*.csv)"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        'Title', 'Channel', 'Status', 'Added', 'Completed', 
                        'Duration', 'Format', 'URL', 'Output Path', 'Error'
                    ])
                    
                    for item in self.queue_manager.get_history():
                        writer.writerow([
                            item.title,
                            item.uploader,
                            item.status.value,
                            item.added_at.strftime("%Y-%m-%d %H:%M:%S"),
                            item.completed_at.strftime("%Y-%m-%d %H:%M:%S") if item.completed_at else "",
                            f"{int(item.duration // 60)}m {int(item.duration % 60)}s" if item.duration else "",
                            item.selected_format or "Auto",
                            item.url,
                            item.output_path,
                            item.error_message or ""
                        ])
                
                QMessageBox.information(self, "Export Complete", f"History exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export history: {str(e)}")
    
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
    
    def show_error(self, error_message: str):
        """Show error message in a dialog"""
        QMessageBox.information(self, "Error Details", error_message)
    
    def closeEvent(self, event):
        """Clean up when dialog is closed"""
        self.refresh_timer.stop()
        super().closeEvent(event)

