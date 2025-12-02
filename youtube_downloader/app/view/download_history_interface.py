# coding: utf-8
from PySide6.QtCore import Qt, Signal, QThread, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from PySide6.QtGui import QDesktopServices

from PySide6.QtWidgets import QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtGui import QColor
from qfluentwidgets import (ScrollArea, PushButton, LineEdit, ComboBox, SwitchButton,
                            ProgressBar, InfoBar, InfoBarPosition, InfoBarIcon,
                            CardWidget, BodyLabel, CaptionLabel, PrimaryPushButton,
                            ToolButton, FluentIcon as FIF, RoundMenu, Action,
                            IndeterminateProgressRing, MessageBox, ListWidget)
import yt_dlp
import os
import time
import threading
from datetime import datetime

from app.common.config import cfg

class DownloadWorker(QThread):
    """ Download worker thread """
    progressUpdated = Signal(int, str)  # progress, video_id
    downloadCompleted = Signal(str, str)  # video_id, file_path
    downloadFailed = Signal(str, str)  # video_id, error_message

    def __init__(self, url, download_path, quality, format_type, is_audio_only):
        super().__init__()
        self.url:str = url
        self.download_path = download_path
        self.quality = quality
        self.format_type = format_type
        self.is_audio_only = is_audio_only
        self._is_cancelled = False

    def run(self):
        try:
            if "playlist" in self.url.lower() or "list=" in self.url.lower():
                self.download_playlist()
            else:
                self.download_video()
        except Exception as e:
            self.downloadFailed.emit("unknown", str(e))

    def download_video(self):
        try:
            # Set up yt-dlp options
            ydl_opts = {
                'format': self.get_format_string(),
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
            }

            if self.is_audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format_type.lower(),
                    'preferredquality': '192',
                }]

            # Ensure download directory exists
            os.makedirs(self.download_path, exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)
                video_id = info_dict.get('id', 'unknown')
                file_path = ydl.prepare_filename(info_dict)

                if not self._is_cancelled:
                    self.downloadCompleted.emit(video_id, file_path)

        except Exception as e:
            self.downloadFailed.emit("unknown", str(e))

    def download_playlist(self):
        try:
            # Set up yt-dlp options for playlist
            ydl_opts = {
                'format': self.get_format_string(),
                'outtmpl': os.path.join(self.download_path, '%(playlist_title)s', '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
            }

            if self.is_audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format_type.lower(),
                    'preferredquality': '192',
                }]

            # Ensure download directory exists
            os.makedirs(self.download_path, exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)

                # Get list of downloaded files
                if 'entries' in info_dict:
                    for entry in info_dict['entries']:
                        if entry and not self._is_cancelled:
                            video_id = entry.get('id', 'unknown')
                            file_path = ydl.prepare_filename(entry)
                            self.downloadCompleted.emit(video_id, file_path)

        except Exception as e:
            self.downloadFailed.emit("unknown", f"Playlist download failed: {str(e)}")

    def get_format_string(self):
        """Get the appropriate format string for yt-dlp"""
        if self.is_audio_only:
            return 'bestaudio/best'

        # Map quality to yt-dlp format selectors
        quality_map = {
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "Best Available": "bestvideo+bestaudio/best"
        }

        format_str = quality_map.get(self.quality, "bestvideo+bestaudio/best")

        # Add format preference if specified
        if self.format_type.lower() != "best":
            format_str += f"/best[ext={self.format_type.lower()}]"

        return format_str

    def progress_hook(self, d):
        """Handle progress updates from yt-dlp"""
        if self._is_cancelled:
            return

        if d['status'] == 'downloading':
            video_id = d.get('info_dict', {}).get('id', 'unknown')
            progress = d.get('_percent_str', '0%').replace('%', '')
            try:
                progress_int = int(float(progress))
                self.progressUpdated.emit(progress_int, video_id)
            except:
                pass

    def cancel(self):
        self._is_cancelled = True

class DownloadHistoryInterface(ScrollArea):
    """ Combined download and history interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('downloadHistoryInterface')

        # Main widget and layout
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        # Download components
        self.urlInput = LineEdit()
        self.qualityCombo = ComboBox()
        self.formatCombo = ComboBox()
        self.audioOnlySwitch = SwitchButton("Audio Only")
        self.downloadBtn = PrimaryPushButton("Download")
        self.progressRing = IndeterminateProgressRing()
        self.progressRing.hide()
        self.progressBar = ProgressBar()

        # History components
        self.historyTable = QTableWidget(self)
        self.clearBtn = PushButton("Clear History", self, FIF.DELETE)

        # Status
        self.statusLabel = BodyLabel("Ready")

        self.__initWidget()
        self.__initLayout()

        # Connect signals
        self.downloadBtn.clicked.connect(self.startDownload)
        self.audioOnlySwitch.checkedChanged.connect(self.updateFormatOptions)
        self.clearBtn.clicked.connect(self.clearHistory)

        # Download worker and tracking
        self.current_worker = None
        self.worker_thread = None
        self.download_history = []

        # Initialize format options
        self.updateFormatOptions()

        # Load existing history
        self.loadHistory()

    def __initWidget(self):
        """ Initialize widgets """
        self.view.setObjectName('view')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        # Configure URL input
        self.urlInput.setPlaceholderText("Enter YouTube URL here...")
        self.urlInput.setClearButtonEnabled(True)

        # Configure quality combo
        self.qualityCombo.addItems(["1080p", "720p", "480p", "360p", "Best Available"])
        self.qualityCombo.setCurrentText(cfg.get(cfg.downloadQuality))

        # Configure format combo
        self.formatCombo.addItems(["MP4", "WEBM", "3GP"])
        self.formatCombo.setCurrentText(cfg.get(cfg.downloadFormat).upper())

        # Configure download button
        self.downloadBtn.setIcon(FIF.DOWNLOAD)

        # Configure progress bar
        self.progressBar.setRange(0, 100)
        self.progressBar.setFixedHeight(6)
        self.progressBar.setVisible(False)

        # Configure history table
        self.historyTable.setObjectName('historyTable')
        self.historyTable.setColumnCount(3)
        self.historyTable.setHorizontalHeaderLabels(['Status', 'Time', 'Details'])
        self.historyTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.historyTable.setAlternatingRowColors(True)
        self.historyTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.historyTable.setEditTriggers(QTableWidget.NoEditTriggers)

    def __initLayout(self):
        """ Initialize layout """
        # URL input row
        urlRow = QHBoxLayout()
        urlRow.addWidget(QLabel("YouTube URL:"))
        urlRow.addWidget(self.urlInput, 1)

        # Options row
        optionsRow = QHBoxLayout()
        optionsRow.addWidget(QLabel("Quality:"))
        optionsRow.addWidget(self.qualityCombo)
        optionsRow.addSpacing(20)
        optionsRow.addWidget(QLabel("Format:"))
        optionsRow.addWidget(self.formatCombo)
        optionsRow.addSpacing(20)
        optionsRow.addWidget(self.audioOnlySwitch)
        optionsRow.addStretch()

        # Download button row
        btnRow = QHBoxLayout()
        btnRow.addWidget(self.progressRing)
        btnRow.addWidget(self.progressBar)
        btnRow.addStretch()
        btnRow.addWidget(self.downloadBtn)

        # Status row
        statusRow = QHBoxLayout()
        statusRow.addWidget(self.statusLabel)
        statusRow.addStretch()

        # History section
        historyTitleRow = QHBoxLayout()
        historyTitleRow.addWidget(QLabel("Download History:"))
        historyTitleRow.addStretch()
        historyTitleRow.addWidget(self.clearBtn)

        # Add to main layout
        self.vBoxLayout.addLayout(urlRow)
        self.vBoxLayout.addLayout(optionsRow)
        self.vBoxLayout.addLayout(btnRow)
        self.vBoxLayout.addLayout(statusRow)
        self.vBoxLayout.addLayout(historyTitleRow)
        self.vBoxLayout.addWidget(self.historyTable, 1)

        # Add info bar for instructions
        self.addInfoBar()

    def addInfoBar(self):
        """ Add information bar with instructions """
        infoBar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Welcome to YouTube Downloader",
            content="Enter a YouTube video or playlist URL above and click Download. "
                   "You can choose quality, format, and download audio-only versions.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=10000,
            parent=self
        )
        infoBar.addWidget(PushButton("Open Example", self))
        self.vBoxLayout.insertWidget(0, infoBar)

    def updateFormatOptions(self):
        """ Update format options based on audio/video selection """
        if self.audioOnlySwitch.isChecked():
            self.formatCombo.clear()
            self.formatCombo.addItems(["MP3", "AAC", "OGG", "WAV"])
            self.formatCombo.setCurrentText("MP3")
        else:
            self.formatCombo.clear()
            self.formatCombo.addItems(["MP4", "WEBM", "3GP"])
            self.formatCombo.setCurrentText(cfg.get(cfg.downloadFormat).upper())

    def startDownload(self):
        """ Start download process """
        url = self.urlInput.text().strip()
        if not url:
            self.showError("Please enter a YouTube URL")
            return

        download_path = cfg.get(cfg.downloadFolder)
        if not download_path or not os.path.exists(download_path):
            # Ask user to select download folder
            download_path = QFileDialog.getExistingDirectory(
                self, "Select Download Folder", QFileDialog.getExistingDirectory()
            )
            if not download_path:
                return
            cfg.set(cfg.downloadFolder, download_path)

        # Validate URL
        if not (url.startswith("http://") or url.startswith("https://")):
            self.showError("Please enter a valid URL starting with http:// or https://")
            return

        # Show progress and start download
        self.statusLabel.setText("Starting download...")
        self.progressRing.show()
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)
        self.downloadBtn.setEnabled(False)

        # Create and start worker thread
        self.current_worker = DownloadWorker(
            url=url,
            download_path=download_path,
            quality=self.qualityCombo.currentText(),
            format_type=self.formatCombo.currentText().lower(),
            is_audio_only=self.audioOnlySwitch.isChecked()
        )

        self.current_worker.progressUpdated.connect(self.updateProgress)
        self.current_worker.downloadCompleted.connect(self.downloadCompleted)
        self.current_worker.downloadFailed.connect(self.downloadFailed)
        self.current_worker.start()

    def updateProgress(self, progress, video_id):
        """ Update download progress """
        self.statusLabel.setText(f"Downloading... {progress}%")
        self.progressBar.setValue(progress)

    def downloadCompleted(self, video_id, file_path):
        """ Handle completed download """
        self.statusLabel.setText("Download completed!")
        self.progressRing.hide()
        self.progressBar.setVisible(False)
        self.downloadBtn.setEnabled(True)

        # Add to history
        self.addToHistory(f"Downloaded: {os.path.basename(file_path)}", "Success")

        # Show success message
        InfoBar.success(
            title='Success',
            content=f'Video downloaded successfully to: {file_path}',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

        # Open file location
        open_folder = MessageBox(
            'Download Complete',
            f'Video downloaded successfully!\n\n{file_path}\n\nOpen download folder?',
            self
        )
        open_folder.yesButton.setText('Open Folder')
        open_folder.cancelButton.setText('Close')
        if open_folder.exec():
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))

    def downloadFailed(self, video_id, error_message):
        """ Handle failed download """
        self.statusLabel.setText(f"Download failed: {error_message}")
        self.progressRing.hide()
        self.progressBar.setVisible(False)
        self.downloadBtn.setEnabled(True)

        # Add to history
        self.addToHistory(f"Failed: {error_message}", "Failed")

        # Show error message
        InfoBar.error(
            title='Download Failed',
            content=f'Failed to download video: {error_message}',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self
        )

    def addToHistory(self, details, status):
        """ Add entry to download history """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create history entry
        entry = {
            'timestamp': timestamp,
            'status': status,
            'details': details
        }

        # Add to history list
        self.download_history.append(entry)

        # Keep history limited
        if len(self.download_history) > cfg.get(cfg.historyLimit):
            self.download_history.pop(0)

        # Save to config
        cfg.set(cfg.downloadHistory, self.download_history)

        # Update display
        self.updateHistoryDisplay()

    def updateHistoryDisplay(self):
        """ Update the history table display """
        self.historyTable.setRowCount(0)  # Clear table
        for entry in reversed(self.download_history):  # Show newest first
            self.addHistoryRow(entry)

    def addHistoryRow(self, entry):
        """ Add history row to table """
        row = self.historyTable.rowCount()
        self.historyTable.insertRow(row)

        # Status column
        status_item = QTableWidgetItem(entry['status'])
        if entry['status'] == 'Success':
            status_item.setBackground(QColor(144, 238, 144))  # Light green
        elif entry['status'] == 'Failed':
            status_item.setBackground(QColor(255, 182, 193))  # Light red
        self.historyTable.setItem(row, 0, status_item)

        # Time column
        time_item = QTableWidgetItem(entry['timestamp'])
        self.historyTable.setItem(row, 1, time_item)

        # Details column
        details_item = QTableWidgetItem(entry['details'])
        self.historyTable.setItem(row, 2, details_item)

    def clearHistory(self):
        """ Clear history """
        self.historyTable.setRowCount(0)
        self.download_history.clear()
        cfg.set(cfg.downloadHistory, [])  # Clear stored history

    def loadHistory(self):
        """ Load history from config """
        try:
            stored_history = cfg.get(cfg.downloadHistory)
            if isinstance(stored_history, list):
                self.download_history = stored_history
                self.updateHistoryDisplay()
        except:
            self.download_history = []

    def showError(self, message):
        """ Show error message """
        InfoBar.error(
            title='Error',
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )

    def showWarning(self, message):
        """ Show warning message """
        InfoBar.warning(
            title='Warning',
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )