from typing import Optional, Dict, Any, List
import os
import shutil
from datetime import datetime

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QPixmap, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QMenu,
    QSizePolicy,
)

from ytdl_worker import YtDlWorker, list_formats, InfoWorker, ThumbWorker
from style import dark_stylesheet  # Updated stylesheet
from subtitle_dialog import SubtitleDialog
from custom_command_dialog import CustomCommandDialog
from download_settings_dialog import DownloadSettingsDialog
from ytdl_worker import PipUpdateWorker
from queue_manager import QueueManager, DownloadItem, DownloadStatus
from queue_dialog import QueueDialog
from history_dialog import HistoryDialog
from loading_widget import LoadingButton


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("YT Downloader")
        self.resize(1024, 720)
        self.setStyleSheet(dark_stylesheet())
        self.setWindowIcon(self._create_icon()) # Simple app icon

        self._central = QWidget()
        self.setCentralWidget(self._central)

        self._layout = QVBoxLayout(self._central)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(15)

        # --- Header bar (URL Input) ---
        header = QHBoxLayout()
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Please paste your video link here")
        self.url_edit.setFixedHeight(40)
        self.analyze_btn = LoadingButton("Search")
        self.analyze_btn.setFixedSize(100, 40)
        self.analyze_btn.setObjectName("AccentButton") # For special styling
        header.addWidget(self.url_edit)
        header.addWidget(self.analyze_btn)
        self._layout.addLayout(header)

        # --- Main content area: thumbnail + metadata + format selection ---
        content_box = QWidget()
        content_box.setObjectName("ContentBox")
        content_layout = QHBoxLayout(content_box)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(320, 180)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("Thumbnail")
        self.thumb_label.setObjectName("ThumbnailLabel")

        meta_vbox = QVBoxLayout()
        meta_vbox.setSpacing(10)
        self.meta_title = QLabel("Video Title")
        self.meta_title.setObjectName("TitleLabel")
        self.meta_title.setWordWrap(True)
        
        self.meta_uploader = QLabel("Channel Name")
        self.meta_uploader.setObjectName("UploaderLabel")
        
        info_hbox = QHBoxLayout()
        self.meta_duration = QLabel("00:00")
        self.meta_views = QLabel("0 views")
        info_hbox.addWidget(self.meta_duration)
        info_hbox.addWidget(self.meta_views)
        info_hbox.addStretch()

        self.format_combo = QComboBox()
        self.format_combo.setFixedHeight(35)
        
        meta_vbox.addWidget(self.meta_title)
        meta_vbox.addWidget(self.meta_uploader)
        meta_vbox.addLayout(info_hbox)
        meta_vbox.addSpacing(10)
        meta_vbox.addWidget(QLabel("Select Quality:"))
        meta_vbox.addWidget(self.format_combo)
        meta_vbox.addStretch()

        content_layout.addWidget(self.thumb_label)
        content_layout.addLayout(meta_vbox)
        self._layout.addWidget(content_box, 1) # Make it stretch

        # --- Footer: Output path and action buttons ---
        footer = QHBoxLayout()
        self.output_label = QLabel("Output: <not set>")
        self.output_label.setObjectName("MutedLabel")
        
        self.settings_btn = QPushButton("Settings & Options")
        self.add_to_queue_btn = QPushButton("Add to Queue")
        self.download_btn = LoadingButton("Download")
        self.download_btn.setObjectName("AccentButton")
        self.download_btn.setFixedHeight(40)
        self.add_to_queue_btn.setFixedHeight(40)
        self.settings_btn.setFixedHeight(40)

        footer.addWidget(self.output_label)
        footer.addStretch()
        footer.addWidget(self.settings_btn)
        footer.addWidget(self.add_to_queue_btn)
        footer.addWidget(self.download_btn)
        self._layout.addLayout(footer)

        # --- Progress Bar ---
        self.progress = QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(10)
        self.progress.setFormat("") # Hide text initially
        self._layout.addWidget(self.progress)

        # --- Signals ---
        self.url_edit.returnPressed.connect(self._analyze)
        self.analyze_btn.clicked.connect(self._analyze)
        self.download_btn.clicked.connect(self._start_download)
        self.add_to_queue_btn.clicked.connect(self._add_to_queue)
        self.settings_btn.clicked.connect(self._open_settings_menu)
        self.format_combo.currentIndexChanged.connect(self._on_format_selected)
        
        # --- State ---
        self.output_dir: Optional[str] = None
        self.last_info: Optional[Dict[str, Any]] = None
        self.worker_thread: Optional[QThread] = None
        self.selected_format: Optional[str] = None
        self.available_subtitles: List[str] = []
        self.selected_subtitles: List[str] = []
        self.ffmpeg_location: Optional[str] = self._detect_ffmpeg()
        self._ffmpeg_warned: bool = False
        self.custom_overrides: Dict[str, str] = {}
        self.settings_overrides: Dict[str, str] = {"concurrent": "4"}
        
        # --- Options State (moved from checkboxes) ---
        self.option_embed_subs = False
        self.option_sponsorblock = False
        self.option_save_thumbnail = False
        self.option_save_description = False

        # --- Queue management ---
        self.queue_manager = QueueManager()
        self.queue_dialog: Optional[QueueDialog] = None
        self.history_dialog: Optional[HistoryDialog] = None

        # --- Setup ---
        self._setup_settings_menu()
        self.output_dir = self._downloads_dir()
        self.output_label.setText(f"Output: {self.output_dir}")
        self._update_ui_state(is_idle=True)

    def _create_icon(self) -> QIcon:
        """Creates a simple QIcon for the window."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        # In a real app, you'd load from a file: QIcon("path/to/icon.png")
        # For this example, we'll just return an empty one.
        return QIcon(pixmap)

    def _setup_settings_menu(self) -> None:
        """Creates the QMenu for the settings button."""
        self.settings_menu = QMenu(self)
        
        # --- File Actions ---
        self.settings_menu.addAction("Choose Output...", self._choose_output)
        self.settings_menu.addAction("Set FFmpeg Location...", self._choose_ffmpeg)
        self.settings_menu.addSeparator()

        # --- Download Options (formerly checkboxes) ---
        self.action_embed_subs = QAction("Merge Subtitles", self, checkable=True)
        self.action_embed_subs.toggled.connect(lambda checked: setattr(self, 'option_embed_subs', checked))
        
        self.action_sponsorblock = QAction("Remove Sponsor Segments", self, checkable=True)
        self.action_sponsorblock.toggled.connect(lambda checked: setattr(self, 'option_sponsorblock', checked))
        
        self.action_save_thumb = QAction("Save Thumbnail", self, checkable=True)
        self.action_save_thumb.toggled.connect(lambda checked: setattr(self, 'option_save_thumbnail', checked))
        
        self.action_save_desc = QAction("Save Description", self, checkable=True)
        self.action_save_desc.toggled.connect(lambda checked: setattr(self, 'option_save_description', checked))
        
        self.settings_menu.addAction(self.action_embed_subs)
        self.settings_menu.addAction(self.action_sponsorblock)
        self.settings_menu.addAction(self.action_save_thumb)
        self.settings_menu.addAction(self.action_save_desc)
        self.settings_menu.addAction("Select Subtitles...", self._pick_subtitles)
        self.settings_menu.addSeparator()

        # --- Tools & Advanced ---
        self.settings_menu.addAction("Download Settings...", self._open_download_settings)
        self.settings_menu.addAction("Custom Command...", self._open_custom_cmd)
        self.settings_menu.addAction("Update yt-dlp...", self._update_ytdlp)
        self.settings_menu.addSeparator()
        self.settings_menu.addAction("View Queue...", self._open_queue)
        self.settings_menu.addAction("View History...", self._open_history)

    def _open_settings_menu(self) -> None:
        """Shows the settings menu under the button."""
        self.settings_menu.popup(self.settings_btn.mapToGlobal(self.settings_btn.rect().bottomLeft()))

    def _update_ui_state(self, is_analyzing: bool = False, is_idle: bool = False, has_info: bool = False):
        """Centralized method to control widget enabled/disabled states."""
        self.url_edit.setEnabled(not is_analyzing)
        self.analyze_btn.setEnabled(not is_analyzing)
        self.download_btn.setEnabled(has_info and not is_analyzing)
        self.add_to_queue_btn.setEnabled(has_info and not is_analyzing)
        self.settings_btn.setEnabled(not is_analyzing)
        self.format_combo.setEnabled(has_info)

        if is_analyzing:
            self.analyze_btn.setLoading(True)
            self.progress.setRange(0, 0)
            self.progress.setFormat("Analyzing...")
        elif is_idle:
            self.analyze_btn.setLoading(False)
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.progress.setFormat("")
        elif has_info:
            self.analyze_btn.setLoading(False)
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.progress.setFormat("")

    def _choose_output(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir = directory
            self.output_label.setText(f"Output: {directory}")

    def _choose_ffmpeg(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Locate ffmpeg executable", "", "ffmpeg (ffmpeg.exe ffmpeg)")
        if path:
            self.ffmpeg_location = os.path.dirname(path)
            os.environ["FFMPEG_LOCATION"] = self.ffmpeg_location
            self.statusBar().showMessage(f"FFmpeg set: {self.ffmpeg_location}", 4000)

    def _analyze(self) -> None:
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please paste a valid video URL.")
            return
        
        self._update_ui_state(is_analyzing=True)
        self._info_worker = InfoWorker(url)
        self._info_worker.info.connect(self._on_info_ready)
        self._info_worker.error.connect(self._on_info_error)
        self._info_worker.start()

    def _on_info_ready(self, info: Dict[str, Any]) -> None:
        self.last_info = info
        self._populate_metadata(info)
        self._populate_formats(list_formats(info))
        subs = sorted(list((info.get("subtitles") or {}).keys()))
        self.available_subtitles = subs
        
        self._update_ui_state(has_info=True)
        self._update_option_states()

    def _on_info_error(self, message: str) -> None:
        self._update_ui_state(is_idle=True)
        QMessageBox.critical(self, "Error", message)

    def _populate_metadata(self, info: Dict[str, Any]) -> None:
        self.meta_title.setText(info.get("title") or "No Title")
        self.meta_uploader.setText(info.get("uploader") or "Unknown Channel")
        
        view_count = info.get("view_count")
        self.meta_views.setText(f"{view_count:,} views" if view_count else "Unknown views")
        
        duration = info.get("duration")
        if duration is not None:
            mins, secs = divmod(int(duration), 60)
            self.meta_duration.setText(f"{mins:02d}:{secs:02d}")
        else:
            self.meta_duration.setText("--:--")
            
        thumb_url = self._get_thumbnail_url()
        if thumb_url:
            self._thumb_worker = ThumbWorker(thumb_url)
            self._thumb_worker.ready.connect(self._on_thumb_ready)
            self._thumb_worker.start()

    def _on_thumb_ready(self, data: bytes) -> None:
        pix = QPixmap()
        if pix.loadFromData(data):
            self.thumb_label.setPixmap(
                pix.scaled(self.thumb_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

    def _populate_formats(self, formats: List[Dict[str, Any]]) -> None:
        self.format_combo.clear()
        
        # Filter and sort formats
        video_formats = [f for f in formats if f.get("vcodec") != "none"]
        audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
        
        # Add video formats first, sorted by resolution
        for f in sorted(video_formats, key=lambda x: x.get("height", 0), reverse=True):
            label = f"{f.get('format_note', '')} ({f.get('ext')})"
            self.format_combo.addItem(label, userData=f)
            
        # Add a separator
        if video_formats and audio_formats:
            self.format_combo.insertSeparator(len(video_formats))
            
        # Add audio formats, sorted by bitrate
        for f in sorted(audio_formats, key=lambda x: x.get("abr", 0), reverse=True):
            label = f"Audio Only - {f.get('format_note', '')} ({f.get('ext')})"
            self.format_combo.addItem(label, userData=f)

    def _on_format_selected(self, index: int):
        if index == -1:
            self.selected_format = None
            return
        
        fmt_data = self.format_combo.itemData(index)
        if not fmt_data:
            self.selected_format = None
            return
        
        format_id = fmt_data.get("format_id")
        vcodec = fmt_data.get("vcodec")
        acodec = fmt_data.get("acodec")
        
        # If format has video but no audio, automatically select best audio to merge
        if vcodec != "none" and acodec == "none":
            self.selected_format = f"{format_id}+bestaudio/best"
        else:
            self.selected_format = format_id

    def _build_ydl_opts(self) -> Dict[str, Any]:
        if not self.selected_format:
            # Default to best if nothing is selected
            format_sel = "bestvideo+bestaudio/best"
        else:
            format_sel = self.selected_format

        # Build output path: Downloads/<Title>/<Title>.<ext>
        base_dir = self.output_dir or self._downloads_dir()
        outtmpl_path = os.path.join(base_dir, "%(title)s", "%(title)s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "format": format_sel,
            "outtmpl": {"default": outtmpl_path},
            "noplaylist": True,
            "concurrent_fragment_downloads": int(self.settings_overrides.get("concurrent", "4")),
            "postprocessors": [],
            "writethumbnail": self.option_save_thumbnail,
            "writesubtitles": bool(self.selected_subtitles),
            "subtitleslangs": self.selected_subtitles or ["en"],
            "embedsubtitles": self.option_embed_subs,
            "writedescription": self.option_save_description,
        }
        
        # Special handling for audio-only formats
        selected_data = self.format_combo.currentData()
        if selected_data and selected_data.get("vcodec") == "none":
             ydl_opts["postprocessors"].append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "0",
            })

        # SponsorBlock
        if self.option_sponsorblock:
            sponsor_categories = ["sponsor", "selfpromo", "interaction", "intro", "outro", "preview", "music_offtopic"]
            ydl_opts["sponsorblock_mark"] = sponsor_categories
            ydl_opts["sponsorblock_remove"] = sponsor_categories

        # Custom overrides (from dialogs)
        # ... (Your existing logic for custom overrides) ...

        # FFmpeg location
        if self.ffmpeg_location:
            ydl_opts["ffmpeg_location"] = self.ffmpeg_location
        
        return ydl_opts

    def _start_download(self) -> None:
        url = self.url_edit.text().strip()
        if not url or not self.last_info:
            QMessageBox.warning(self, "No Video", "Please analyze a video first.")
            return
        
        ydl_opts = self._build_ydl_opts()
        self.progress.setFormat("Starting download…")
        self._run_worker(url, ydl_opts)

    def _run_worker(self, url: str, ydl_opts: Dict[str, Any]) -> None:
        if self.worker_thread is not None and self.worker_thread.isRunning():
            QMessageBox.warning(self, "In Progress", "A download is already running.")
            return
            
        # Set download button to loading state
        self.download_btn.setLoading(True)
        self._update_ui_state(is_analyzing=True) # Visually disable UI during download
        self.worker_thread = YtDlWorker(url, ydl_opts)
        self.worker_thread.progress.connect(self._on_progress)
        self.worker_thread.error.connect(self._on_error)
        self.worker_thread.done.connect(self._on_done)
        self.worker_thread.start()

    def _on_progress(self, pct: int, speed: str, eta: str) -> None:
        self.progress.setValue(pct)
        if pct == 100:
            self.progress.setFormat("Processing...")
        else:
            self.progress.setFormat(f"{pct}% ({speed}) ETA {eta}")

    def _on_error(self, message: str) -> None:
        self.download_btn.setLoading(False)
        self._update_ui_state(has_info=True) # Re-enable UI
        self.progress.setValue(0)
        self.progress.setFormat("Error")
        QMessageBox.critical(self, "Download error", message)
        self.worker_thread = None

    def _on_done(self, ok: bool, message: str) -> None:
        self.download_btn.setLoading(False)
        self._update_ui_state(has_info=True) # Re-enable UI
        self.progress.setValue(100 if ok else 0)
        self.progress.setFormat("Done!" if ok else "Failed")
        if ok:
            QMessageBox.information(self, "Download Complete", message)
        else:
            QMessageBox.critical(self, "Download Failed", message)
        self.worker_thread = None

    def _downloads_dir(self) -> str:
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

    def _update_option_states(self) -> None:
        has_ffmpeg = bool(self._detect_ffmpeg())
        has_subs = bool(self.available_subtitles)
        can_embed = has_ffmpeg and has_subs
        self.action_embed_subs.setEnabled(can_embed)
        if not can_embed:
            self.action_embed_subs.setChecked(False)
            self.action_embed_subs.setToolTip("Requires FFmpeg and available subtitles.")
        else:
            self.action_embed_subs.setToolTip("")

    def _detect_ffmpeg(self) -> Optional[str]:
        # (This function remains the same as your original)
        env = os.environ.get("FFMPEG_LOCATION")
        if env and os.path.exists(env): return env
        exe = shutil.which("ffmpeg")
        if exe: return os.path.dirname(exe)
        return None

    def _pick_subtitles(self) -> None:
        if not self.available_subtitles:
            QMessageBox.information(self, "Subtitles", "No subtitles available for this video.")
            return
        dlg = SubtitleDialog(self.available_subtitles, self.selected_subtitles, self)
        if dlg.exec():
            self.selected_subtitles = dlg.selected()
            self.statusBar().showMessage(f"Subtitles selected: {', '.join(self.selected_subtitles) or 'None'}", 3000)

    def _open_custom_cmd(self) -> None:
        dlg = CustomCommandDialog(self)
        if dlg.exec():
            self.custom_overrides = dlg.values()
            self.statusBar().showMessage("Custom options applied", 3000)

    def _open_download_settings(self) -> None:
        dlg = DownloadSettingsDialog(self.settings_overrides, self)
        if dlg.exec():
            self.settings_overrides.update(dlg.values())
            self.statusBar().showMessage("Download settings saved", 3000)

    def _update_ytdlp(self) -> None:
        self._update_ui_state(is_analyzing=True)
        self.progress.setFormat("Updating yt-dlp...")
        self._pip = PipUpdateWorker()
        self._pip.done.connect(self._on_pip_done)
        self._pip.start()

    def _on_pip_done(self, ok: bool, msg: str) -> None:
        self._update_ui_state(has_info=bool(self.last_info))
        if ok:
            QMessageBox.information(self, "Update Complete", msg)
        else:
            QMessageBox.critical(self, "Update Failed", msg)
    
    def _add_to_queue(self) -> None:
        # (This function remains the same as your original)
        if not self.last_info:
            QMessageBox.warning(self, "No Video", "Please analyze a video first.")
            return
        url = self.url_edit.text().strip()
        ydl_opts = self._build_ydl_opts()
        item = DownloadItem(
            url=url, title=self.last_info.get("title", "Unknown"),
            uploader=self.last_info.get("uploader", "Unknown"),
            duration=self.last_info.get("duration"),
            thumbnail_url=self._get_thumbnail_url(),
            selected_format=self.selected_format,
            output_path=ydl_opts.get("outtmpl", {}).get("default", ""),
            options=ydl_opts, status=DownloadStatus.PENDING,
            added_at=datetime.now()
        )
        self.queue_manager.add_to_queue(item)
        QMessageBox.information(self, "Added to Queue", f"'{item.title}' added to download queue.")
    
    def _open_queue(self) -> None:
        if not self.queue_dialog:
            self.queue_dialog = QueueDialog(self.queue_manager, self)
        self.queue_dialog.show()
    
    def _open_history(self) -> None:
        if not self.history_dialog:
            self.history_dialog = HistoryDialog(self.queue_manager, self)
        self.history_dialog.show()
    
    def _get_thumbnail_url(self) -> Optional[str]:
        if not self.last_info: return None
        thumbs = self.last_info.get("thumbnails") or []
        if thumbs:
            return sorted(thumbs, key=lambda t: t.get("width", 0))[-1].get("url")
        return None

