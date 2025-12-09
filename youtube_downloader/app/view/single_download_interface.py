# coding: utf-8
"""
Single Video Download Interface
"""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QFrame)
from PySide6.QtGui import QDesktopServices, QColor, QKeySequence, QShortcut

from qfluentwidgets import (ScrollArea, PushButton, LineEdit, ComboBox, SwitchButton,
                            ProgressBar, InfoBar, InfoBarPosition, InfoBarIcon,
                            CardWidget, BodyLabel, CaptionLabel, PrimaryPushButton,
                            FluentIcon as FIF, IndeterminateProgressRing, MessageBox,
                            StrongBodyLabel, SubtitleLabel)
import os

from app.common.config import cfg
from app.common.utils import extract_video_id_from_url, is_playlist_only_url
from app.components.download_worker import DownloadWorker


class SingleDownloadInterface(ScrollArea):
    """ Single video download interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('singleDownloadInterface')

        # Main widget and layout
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        # Download components
        self.urlInput = LineEdit()
        self.qualityCombo = ComboBox()
        self.formatCombo = ComboBox()
        self.audioOnlySwitch = SwitchButton("Audio Only")
        self.downloadBtn = PrimaryPushButton("Download")
        self.cancelBtn = PushButton("Cancel", self, FIF.CANCEL)
        self.cancelBtn.hide()
        self.progressRing = IndeterminateProgressRing()
        self.progressRing.hide()
        self.progressBar = ProgressBar()
        
        # Video info card
        self.videoInfoCard = CardWidget(self)
        self.videoInfoCard.hide()
        self.videoTitleLabel = StrongBodyLabel("Video Title")
        self.videoDurationLabel = CaptionLabel("Duration: --:--")
        
        # Enhanced status
        self.statusLabel = BodyLabel("Ready to download")
        self.speedLabel = CaptionLabel("")
        self.etaLabel = CaptionLabel("")

        self.__initWidget()
        self.__initLayout()

        # Connect signals
        self.downloadBtn.clicked.connect(self.startDownload)
        self.cancelBtn.clicked.connect(self.cancelDownload)
        self.audioOnlySwitch.checkedChanged.connect(self.updateFormatOptions)
        
        # Keyboard shortcuts
        self.downloadShortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.downloadShortcut.activated.connect(self.startDownload)
        self.cancelShortcut = QShortcut(QKeySequence("Escape"), self)
        self.cancelShortcut.activated.connect(self.cancelDownload)

        # Download worker and tracking
        self.current_worker = None
        self.worker_thread = None

        # Initialize format options
        self.updateFormatOptions()

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
        self.urlInput.setPlaceholderText("Enter YouTube URL here (Ctrl+Enter to download)...")
        self.urlInput.setClearButtonEnabled(True)
        self.urlInput.setMinimumHeight(40)

        # Configure quality combo
        self.qualityCombo.addItems(["Best Available", "1080p", "720p", "480p", "360p"])
        self.qualityCombo.setCurrentText(cfg.get(cfg.downloadQuality))
        self.qualityCombo.setMinimumWidth(150)

        # Configure format combo
        self.formatCombo.addItems(["WEBM", "MP4", "MKV"])
        self.formatCombo.setCurrentText("WEBM")  # Default to WEBM (native format)
        self.formatCombo.setMinimumWidth(120)
        self.formatCombo.currentTextChanged.connect(self.onFormatChanged)

        # Configure download button
        self.downloadBtn.setIcon(FIF.DOWNLOAD)
        self.downloadBtn.setMinimumHeight(36)
        
        # Configure cancel button
        self.cancelBtn.setMinimumHeight(36)

        # Configure progress bar
        self.progressBar.setRange(0, 100)
        self.progressBar.setFixedHeight(8)
        self.progressBar.setVisible(False)
        
        # Configure video info card
        videoInfoLayout = QVBoxLayout(self.videoInfoCard)
        videoInfoLayout.setContentsMargins(15, 15, 15, 15)
        videoInfoLayout.setSpacing(8)
        videoInfoLayout.addWidget(self.videoTitleLabel)
        videoInfoLayout.addWidget(self.videoDurationLabel)
        
        # Configure status labels
        self.speedLabel.setTextColor(QColor(100, 100, 100), QColor(200, 200, 200))
        self.etaLabel.setTextColor(QColor(100, 100, 100), QColor(200, 200, 200))

    def __initLayout(self):
        """ Initialize layout """
        # Create download card
        downloadCard = CardWidget(self)
        downloadCardLayout = QVBoxLayout(downloadCard)
        downloadCardLayout.setContentsMargins(20, 20, 20, 20)
        downloadCardLayout.setSpacing(15)
        
        # Title
        titleLabel = SubtitleLabel("Download Video")
        downloadCardLayout.addWidget(titleLabel)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        downloadCardLayout.addWidget(separator)
        
        # URL input row
        urlRow = QHBoxLayout()
        urlLabel = BodyLabel("URL:")
        urlLabel.setFixedWidth(60)
        urlRow.addWidget(urlLabel)
        urlRow.addWidget(self.urlInput, 1)
        downloadCardLayout.addLayout(urlRow)

        # Options row
        optionsRow = QHBoxLayout()
        qualityLabel = BodyLabel("Quality:")
        qualityLabel.setFixedWidth(60)
        optionsRow.addWidget(qualityLabel)
        optionsRow.addWidget(self.qualityCombo)
        optionsRow.addSpacing(15)
        formatLabel = BodyLabel("Format:")
        formatLabel.setFixedWidth(60)
        optionsRow.addWidget(formatLabel)
        optionsRow.addWidget(self.formatCombo)
        optionsRow.addSpacing(15)
        optionsRow.addWidget(self.audioOnlySwitch)
        optionsRow.addStretch()
        downloadCardLayout.addLayout(optionsRow)
        
        # Video info card
        downloadCardLayout.addWidget(self.videoInfoCard)

        # Progress section
        progressLayout = QVBoxLayout()
        progressLayout.setSpacing(8)
        
        # Progress bar
        progressLayout.addWidget(self.progressBar)
        
        # Status row with speed and ETA
        statusRow = QHBoxLayout()
        statusRow.addWidget(self.statusLabel)
        statusRow.addStretch()
        statusRow.addWidget(self.speedLabel)
        statusRow.addSpacing(15)
        statusRow.addWidget(self.etaLabel)
        progressLayout.addLayout(statusRow)
        
        downloadCardLayout.addLayout(progressLayout)

        # Download button row
        btnRow = QHBoxLayout()
        btnRow.addWidget(self.progressRing)
        btnRow.addStretch()
        btnRow.addWidget(self.cancelBtn)
        btnRow.addWidget(self.downloadBtn)
        downloadCardLayout.addLayout(btnRow)

        # Add download card to main layout
        self.vBoxLayout.addWidget(downloadCard)

        # Add info bar for instructions
        self.addInfoBar()

    def addInfoBar(self):
        """ Add information bar with instructions """
        infoBar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Welcome to YouTube Downloader",
            content="Enter a YouTube video URL and press Ctrl+Enter or click Download. "
                   "Choose quality, format, and enable audio-only mode as needed.",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=8000,
            parent=self
        )
        self.vBoxLayout.insertWidget(0, infoBar)

    def updateFormatOptions(self):
        """ Update format options based on audio/video selection """
        if self.audioOnlySwitch.isChecked():
            self.formatCombo.clear()
            self.formatCombo.addItems(["MP3", "M4A", "OPUS", "OGG", "WAV"])
            self.formatCombo.setCurrentText("MP3")
            self.formatCombo.setToolTip("Audio will be extracted and converted to selected format")
        else:
            self.formatCombo.clear()
            self.formatCombo.addItems(["WEBM", "MP4", "MKV"])
            self.formatCombo.setCurrentText("WEBM")
            self.formatCombo.setToolTip("WEBM is YouTube's native format (fastest). MP4/MKV may require conversion.")
    
    def onFormatChanged(self, format_text):
        """ Handle format selection change """
        if not self.audioOnlySwitch.isChecked() and format_text == "MP4":
            InfoBar.warning(
                title='Format Notice',
                content='MP4 format may require conversion using FFmpeg, which can take additional time. WEBM is recommended for faster downloads.',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=4000,
                parent=self
            )

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
        
        # Check if it's a pure playlist URL (without video ID)
        if is_playlist_only_url(url):
            self.showError("This is a playlist URL. Please use the Playlist tab to download playlists.")
            return
        
        # Extract clean video URL (remove playlist parameters)
        clean_url, video_id = extract_video_id_from_url(url)
        if not clean_url:
            self.showError("Could not extract video ID from URL. Please check the URL format.")
            return
        
        # Use the clean URL for download
        url = clean_url

        # Add to history immediately with "Downloading" status
        self.current_history_index = self.addToHistory(url, "Downloading", "")

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
        self.current_worker.videoInfoFetched.connect(self.showVideoInfo)
        self.current_worker.start()
        
        # Show cancel button
        self.cancelBtn.show()

    def updateProgress(self, progress, video_id, speed, eta):
        """ Update download progress """
        self.statusLabel.setText(f"Downloading... {progress}%")
        self.progressBar.setValue(progress)
        self.speedLabel.setText(f"Speed: {speed}")
        self.etaLabel.setText(f"ETA: {eta}")

    def downloadCompleted(self, video_id, file_path, title):
        """ Handle completed download """
        self.statusLabel.setText("Download completed!")
        self.progressRing.hide()
        self.progressBar.setVisible(False)
        self.speedLabel.setText("")
        self.etaLabel.setText("")
        self.downloadBtn.setEnabled(True)
        self.cancelBtn.hide()
        self.videoInfoCard.hide()

        # Update history entry
        self.updateHistoryEntry(self.current_history_index, title, "Success", file_path)

        # Show success message
        InfoBar.success(
            title='Download Complete',
            content=f'{title} downloaded successfully!',
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
        self.statusLabel.setText("Download failed")
        self.progressRing.hide()
        self.progressBar.setVisible(False)
        self.speedLabel.setText("")
        self.etaLabel.setText("")
        self.downloadBtn.setEnabled(True)
        self.cancelBtn.hide()
        self.videoInfoCard.hide()

        # Update history entry
        self.updateHistoryEntry(self.current_history_index, error_message, "Failed", "")

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

    def addToHistory(self, title, status, file_path):
        """ Add entry to download history and return its index """
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create history entry
        entry = {
            'timestamp': timestamp,
            'status': status,
            'title': title,
            'path': file_path,
            'type': 'single'
        }

        # Get existing history
        download_history = cfg.get(cfg.downloadHistory) or []
        
        # Add to history list
        download_history.append(entry)
        history_index = len(download_history) - 1

        # Keep history limited
        if len(download_history) > cfg.get(cfg.historyLimit):
            download_history.pop(0)
            history_index -= 1

        # Save to config
        cfg.set(cfg.downloadHistory, download_history)
        
        # Notify history interface to refresh
        self.notifyHistoryUpdate()
        
        return history_index
    
    def updateHistoryEntry(self, index, title, status, file_path):
        """ Update existing history entry """
        download_history = cfg.get(cfg.downloadHistory) or []
        
        if 0 <= index < len(download_history):
            download_history[index]['title'] = title
            download_history[index]['status'] = status
            download_history[index]['path'] = file_path
            cfg.set(cfg.downloadHistory, download_history)
            
            # Notify history interface to refresh
            self.notifyHistoryUpdate()
    
    def notifyHistoryUpdate(self):
        """ Notify history interface to refresh """
        # Find history interface and refresh it
        main_window = self.window()
        if hasattr(main_window, 'historyInterface'):
            main_window.historyInterface.refreshHistory()

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
    
    def cancelDownload(self):
        """ Cancel current download """
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait()
            self.statusLabel.setText("Download cancelled")
            self.progressRing.hide()
            self.progressBar.setVisible(False)
            self.speedLabel.setText("")
            self.etaLabel.setText("")
            self.downloadBtn.setEnabled(True)
            self.cancelBtn.hide()
            self.videoInfoCard.hide()
            
            # Update history entry to cancelled
            if hasattr(self, 'current_history_index'):
                self.updateHistoryEntry(self.current_history_index, "Cancelled", "Cancelled", "")
            
            InfoBar.warning(
                title='Cancelled',
                content='Download was cancelled by user',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self
            )
    
    def showVideoInfo(self, title, duration, thumbnail_url):
        """ Show video information """
        self.videoTitleLabel.setText(title)
        try:
            duration_int = int(duration)
            minutes = duration_int // 60
            seconds = duration_int % 60
            self.videoDurationLabel.setText(f"Duration: {minutes}:{seconds:02d}")
        except:
            self.videoDurationLabel.setText("Duration: Unknown")
        self.videoInfoCard.show()
    

