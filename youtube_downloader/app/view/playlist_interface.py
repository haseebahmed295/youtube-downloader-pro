# coding: utf-8
"""
Playlist Download Interface with individual file tracking
"""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFileDialog, QFrame)
from PySide6.QtGui import QDesktopServices, QColor

from qfluentwidgets import (ScrollArea, PushButton, LineEdit, ComboBox,
                            ProgressBar, InfoBar, InfoBarPosition,
                            CardWidget, BodyLabel, CaptionLabel, PrimaryPushButton,
                            FluentIcon as FIF, IndeterminateProgressRing,
                            StrongBodyLabel, SubtitleLabel, SwitchButton, SpinBox,
                            CheckBox, IconInfoBadge, InfoBadge, DotInfoBadge)
import os

from app.common.config import cfg
from app.common.utils import clean_unicode_text
from app.components.concurrent_playlist_worker import ConcurrentPlaylistWorker


class PlaylistFileCard(CardWidget):
    """Card widget for displaying individual file download progress"""
    
    def __init__(self, index, total, title, parent=None):
        super().__init__(parent)
        self.index = index
        self.title = title
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        # Title row
        self.titleRow = QHBoxLayout()
        
        # Index badge instead of text label
        self.indexBadge = InfoBadge.info(f"{index}/{total}")
        self.titleLabel = BodyLabel(title)
        
        # Status badge instead of text
        self.statusBadge = DotInfoBadge.attension()
        self.statusLabel = CaptionLabel("Waiting...")
        
        self.titleRow.addWidget(self.indexBadge)
        self.titleRow.addWidget(self.titleLabel, 1)
        self.titleRow.addWidget(self.statusBadge)
        self.titleRow.addWidget(self.statusLabel)
        
        # Progress bar
        self.progressBar = ProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setFixedHeight(6)
        
        # Info row
        infoRow = QHBoxLayout()
        self.speedLabel = CaptionLabel("")
        self.etaLabel = CaptionLabel("")
        
        infoRow.addWidget(self.speedLabel)
        infoRow.addStretch()
        infoRow.addWidget(self.etaLabel)
        
        layout.addLayout(self.titleRow)
        layout.addWidget(self.progressBar)
        layout.addLayout(infoRow)
        
    def updateProgress(self, progress, speed, eta):
        """Update progress display"""
        self.progressBar.setValue(progress)
        
        # Show progress percentage in status label as badge-style text
        self.statusLabel.setText(f"{progress}%")
        self.statusLabel.setStyleSheet("color: #0078D4; font-weight: bold;")
        
        self.speedLabel.setText(f"Speed: {speed}")
        self.etaLabel.setText(f"ETA: {eta}")
        
        # Update badge color based on progress
        if progress < 30:
            # Keep attention badge for low progress
            pass
        elif progress < 70:
            # Change to info badge for medium progress
            index = self.titleRow.indexOf(self.statusBadge)
            if index >= 0:
                self.statusBadge.deleteLater()
                self.statusBadge = DotInfoBadge.info()
                self.titleRow.insertWidget(index, self.statusBadge)
        
    def setCompleted(self):
        """Mark as completed"""
        self.progressBar.setValue(100)
        
        # Replace badge with success badge
        index = self.titleRow.indexOf(self.statusBadge)
        if index >= 0:
            self.statusBadge.deleteLater()
            self.statusBadge = IconInfoBadge.success(FIF.ACCEPT_MEDIUM)
            self.titleRow.insertWidget(index, self.statusBadge)
        
        self.statusLabel.setText("Complete")
        self.statusLabel.setStyleSheet("color: #10893E;")
        self.speedLabel.setText("")
        self.etaLabel.setText("")
        
    def setFailed(self, error):
        """Mark as failed"""
        # Replace badge with error badge
        index = self.titleRow.indexOf(self.statusBadge)
        if index >= 0:
            self.statusBadge.deleteLater()
            self.statusBadge = IconInfoBadge.error(FIF.CANCEL_MEDIUM)
            self.titleRow.insertWidget(index, self.statusBadge)
        
        self.statusLabel.setText("Failed")
        self.statusLabel.setStyleSheet("color: #D13438;")
        
        # Clean error message to remove unsupported Unicode characters
        clean_error = clean_unicode_text(error) if error else "Unknown error"
        self.speedLabel.setText(clean_error[:50])
        self.etaLabel.setText("")


class PlaylistInterface(ScrollArea):
    """Playlist download interface with individual file tracking"""
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('playlistInterface')
        
        # Main widget
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        
        # Components
        self.urlInput = LineEdit()
        self.qualityCombo = ComboBox()
        self.formatCombo = ComboBox()
        self.audioOnlySwitch = SwitchButton("Audio Only")
        
        # Playlist options
        self.startIndexSpin = SpinBox()
        self.endIndexSpin = SpinBox()
        self.subtitlesCheck = CheckBox("Download Subtitles")
        
        # Advanced options
        self.concurrentSpin = SpinBox()
        self.speedLimitSpin = SpinBox()
        
        # Buttons
        self.downloadBtn = PrimaryPushButton("Download Playlist")
        self.cancelBtn = PushButton("Cancel", self, FIF.CANCEL)
        self.cancelBtn.hide()
        
        # Progress
        self.progressRing = IndeterminateProgressRing()
        self.progressRing.hide()
        self.statusLabel = BodyLabel("Ready to download playlist")
        self.currentDownloadLabel = CaptionLabel("")
        self.downloadProgressBadge = None
        
        # Playlist info
        self.playlistTitleLabel = StrongBodyLabel("")
        self.playlistCountLabel = CaptionLabel("")
        
        # Statistics badges
        self.successBadge = None
        self.failBadge = None
        self.totalBadge = None
        
        # File cards container
        self.fileCardsWidget = QWidget()
        self.fileCardsLayout = QVBoxLayout(self.fileCardsWidget)
        self.fileCardsLayout.setSpacing(10)
        self.fileCardsLayout.setAlignment(Qt.AlignTop)
        
        self.file_cards = {}  # index -> card
        self.current_worker = None
        
        self.__initWidget()
        self.__initLayout()
        
        # Connect signals
        self.downloadBtn.clicked.connect(self.startDownload)
        self.cancelBtn.clicked.connect(self.cancelDownload)
        self.audioOnlySwitch.checkedChanged.connect(self.updateFormatOptions)
        
        self.updateFormatOptions()
        
    def __initWidget(self):
        """Initialize widgets"""
        self.view.setObjectName('view')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        
        # URL input
        self.urlInput.setPlaceholderText("Enter YouTube playlist URL...")
        self.urlInput.setClearButtonEnabled(True)
        self.urlInput.setMinimumHeight(40)
        
        # Quality combo
        self.qualityCombo.addItems(["Best Available", "1080p", "720p", "480p", "360p"])
        self.qualityCombo.setCurrentText(cfg.get(cfg.downloadQuality))
        self.qualityCombo.setMinimumWidth(150)
        
        # Format combo
        self.formatCombo.addItems(["WEBM", "MP4", "MKV"])
        self.formatCombo.setCurrentText("WEBM")  # Default to WEBM (native format)
        self.formatCombo.setMinimumWidth(120)
        self.formatCombo.setToolTip("WEBM is YouTube's native format (fastest). MP4/MKV may require conversion.")
        self.formatCombo.currentTextChanged.connect(self.onFormatChanged)
        
        # Playlist range with modern SpinBox
        self.startIndexSpin.setMinimum(1)
        self.startIndexSpin.setMaximum(9999)
        self.startIndexSpin.setValue(1)
        self.startIndexSpin.setPrefix("From: ")
        self.startIndexSpin.setAccelerated(True)  # Enable acceleration
        self.startIndexSpin.setMinimumWidth(120)
        
        self.endIndexSpin.setMinimum(0)
        self.endIndexSpin.setMaximum(9999)
        self.endIndexSpin.setValue(0)
        self.endIndexSpin.setPrefix("To: ")
        self.endIndexSpin.setSpecialValueText("End")
        self.endIndexSpin.setAccelerated(True)  # Enable acceleration
        self.endIndexSpin.setMinimumWidth(120)
        
        # Advanced options
        self.concurrentSpin.setMinimum(1)
        self.concurrentSpin.setMaximum(5)
        self.concurrentSpin.setValue(cfg.get(cfg.concurrentPlaylistDownloads))
        self.concurrentSpin.setPrefix("Concurrent: ")
        self.concurrentSpin.setAccelerated(True)
        self.concurrentSpin.setMinimumWidth(140)
        
        self.speedLimitSpin.setMinimum(0)
        self.speedLimitSpin.setMaximum(100)
        self.speedLimitSpin.setValue(cfg.get(cfg.speedLimit))
        self.speedLimitSpin.setPrefix("Limit: ")
        self.speedLimitSpin.setSuffix(" MB/s")
        self.speedLimitSpin.setSpecialValueText("Unlimited")
        self.speedLimitSpin.setAccelerated(True)
        self.speedLimitSpin.setMinimumWidth(150)
        
        # Buttons
        self.downloadBtn.setIcon(FIF.DOWNLOAD)
        self.downloadBtn.setMinimumHeight(36)
        self.cancelBtn.setMinimumHeight(36)
        
    def __initLayout(self):
        """Initialize layout"""
        # Main card
        mainCard = CardWidget(self)
        mainLayout = QVBoxLayout(mainCard)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        mainLayout.setSpacing(15)
        
        # Title
        titleLabel = SubtitleLabel("Download Playlist")
        mainLayout.addWidget(titleLabel)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        mainLayout.addWidget(separator)
        
        # URL row
        urlRow = QHBoxLayout()
        urlLabel = BodyLabel("Playlist URL:")
        urlLabel.setFixedWidth(100)
        urlRow.addWidget(urlLabel)
        urlRow.addWidget(self.urlInput, 1)
        mainLayout.addLayout(urlRow)
        
        # Quality and format row
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
        mainLayout.addLayout(optionsRow)
        
        # Playlist options row
        playlistRow = QHBoxLayout()
        playlistRow.addWidget(self.startIndexSpin)
        playlistRow.addWidget(self.endIndexSpin)
        playlistRow.addSpacing(15)
        playlistRow.addWidget(self.subtitlesCheck)
        playlistRow.addStretch()
        mainLayout.addLayout(playlistRow)
        
        # Advanced options row
        advancedRow = QHBoxLayout()
        advancedRow.addWidget(self.concurrentSpin)
        advancedRow.addWidget(self.speedLimitSpin)
        advancedRow.addStretch()
        mainLayout.addLayout(advancedRow)
        
        # Status row with download progress badge
        statusRow = QHBoxLayout()
        statusRow.addWidget(self.statusLabel)
        statusRow.addSpacing(10)
        
        # Add download progress badge (shows "X/Y" in a badge)
        self.downloadProgressBadge = InfoBadge.attension(0)
        self.downloadProgressBadge.hide()
        statusRow.addWidget(self.downloadProgressBadge)
        
        statusRow.addStretch()
        
        # Add current download label (will show video title)
        self.currentDownloadLabel = CaptionLabel("")
        self.currentDownloadLabel.setStyleSheet("color: #0078D4;")
        statusRow.addWidget(self.currentDownloadLabel)
        
        mainLayout.addLayout(statusRow)
        
        # Buttons row
        btnRow = QHBoxLayout()
        btnRow.addWidget(self.progressRing)
        btnRow.addStretch()
        btnRow.addWidget(self.cancelBtn)
        btnRow.addWidget(self.downloadBtn)
        mainLayout.addLayout(btnRow)
        
        self.vBoxLayout.addWidget(mainCard)
        
        # Playlist info card
        infoCard = CardWidget(self)
        infoLayout = QVBoxLayout(infoCard)
        infoLayout.setContentsMargins(20, 15, 20, 15)
        infoLayout.addWidget(self.playlistTitleLabel)
        
        # Count row with badges
        countRow = QHBoxLayout()
        countRow.addWidget(self.playlistCountLabel)
        countRow.addStretch()
        
        # Statistics badges with labels
        self.badgesLayout = QHBoxLayout()
        self.badgesLayout.setSpacing(15)
        
        # Total badge with label
        totalContainer = QHBoxLayout()
        totalContainer.setSpacing(5)
        self.totalBadgeLabel = CaptionLabel("Total:")
        totalContainer.addWidget(self.totalBadgeLabel)
        self.badgesLayout.addLayout(totalContainer)
        
        # Success badge with label
        successContainer = QHBoxLayout()
        successContainer.setSpacing(5)
        self.successBadgeLabel = CaptionLabel("Success:")
        successContainer.addWidget(self.successBadgeLabel)
        self.badgesLayout.addLayout(successContainer)
        
        # Fail badge with label
        failContainer = QHBoxLayout()
        failContainer.setSpacing(5)
        self.failBadgeLabel = CaptionLabel("Failed:")
        failContainer.addWidget(self.failBadgeLabel)
        self.badgesLayout.addLayout(failContainer)
        
        countRow.addLayout(self.badgesLayout)
        infoLayout.addLayout(countRow)
        
        infoCard.hide()
        self.playlistInfoCard = infoCard
        self.vBoxLayout.addWidget(infoCard)
        
        # File cards
        self.vBoxLayout.addWidget(self.fileCardsWidget)
        
    def updateFormatOptions(self):
        """Update format options based on audio/video selection"""
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
        """Handle format selection change"""
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
        """Start playlist download"""
        url = self.urlInput.text().strip()
        if not url:
            InfoBar.error(
                title='Error',
                content="Please enter a playlist URL",
                parent=self
            )
            return
            
        download_path = cfg.get(cfg.downloadFolder)
        if not download_path or not os.path.exists(download_path):
            download_path = QFileDialog.getExistingDirectory(
                self, "Select Download Folder"
            )
            if not download_path:
                return
            cfg.set(cfg.downloadFolder, download_path)
            
        # Clear previous cards
        for card in self.file_cards.values():
            card.deleteLater()
        self.file_cards.clear()
        
        # Clear previous badges
        if self.successBadge:
            self.successBadge.deleteLater()
            self.successBadge = None
        if self.failBadge:
            self.failBadge.deleteLater()
            self.failBadge = None
        if self.totalBadge:
            self.totalBadge.deleteLater()
            self.totalBadge = None
        
        # Add to history immediately with "Downloading" status
        self.current_history_index = self.addToHistoryStart(url)
        
        # Show progress
        self.statusLabel.setText("Fetching playlist info...")
        self.progressRing.show()
        self.downloadBtn.setEnabled(False)
        self.cancelBtn.show()
        
        # Create worker with concurrent downloads
        end_index = self.endIndexSpin.value() if self.endIndexSpin.value() > 0 else None
        concurrent = self.concurrentSpin.value() if hasattr(self, 'concurrentSpin') else cfg.get(cfg.concurrentPlaylistDownloads)
        speed_limit = self.speedLimitSpin.value() if hasattr(self, 'speedLimitSpin') else cfg.get(cfg.speedLimit)
        
        self.current_worker = ConcurrentPlaylistWorker(
            url=url,
            download_path=download_path,
            quality=self.qualityCombo.currentText(),
            format_type=self.formatCombo.currentText().lower(),
            is_audio_only=self.audioOnlySwitch.isChecked(),
            start_index=self.startIndexSpin.value(),
            end_index=end_index,
            download_subtitles=self.subtitlesCheck.isChecked(),
            concurrent_downloads=concurrent,
            speed_limit=speed_limit
        )
        
        # Connect signals
        self.current_worker.playlistInfoFetched.connect(self.onPlaylistInfo)
        self.current_worker.fileStarted.connect(self.onFileStarted)
        self.current_worker.fileProgress.connect(self.onFileProgress)
        self.current_worker.fileCompleted.connect(self.onFileCompleted)
        self.current_worker.fileFailed.connect(self.onFileFailed)
        self.current_worker.playlistCompleted.connect(self.onPlaylistCompleted)
        
        self.current_worker.start()
        
    def onPlaylistInfo(self, title, count):
        """Handle playlist info"""
        # Clean title to remove unsupported Unicode characters
        clean_title = clean_unicode_text(title) if title else "Playlist"
        self.playlistTitleLabel.setText(f"Playlist: {clean_title}")
        self.playlistCountLabel.setText("")  # Remove text, badges will show the info
        
        # Update history with actual playlist title
        download_history = cfg.get(cfg.downloadHistory) or []
        if 0 <= self.current_history_index < len(download_history):
            download_history[self.current_history_index]['title'] = clean_title
            cfg.set(cfg.downloadHistory, download_history)
            self.notifyHistoryUpdate()
        
        # Add badges to their respective containers
        # Total badge
        self.totalBadge = InfoBadge.info(count)
        totalContainer = self.badgesLayout.itemAt(0).layout()
        totalContainer.addWidget(self.totalBadge)
        
        # Success badge
        self.successBadge = InfoBadge.success(0)
        successContainer = self.badgesLayout.itemAt(1).layout()
        successContainer.addWidget(self.successBadge)
        
        # Fail badge
        self.failBadge = InfoBadge.error(0)
        failContainer = self.badgesLayout.itemAt(2).layout()
        failContainer.addWidget(self.failBadge)
        
        self.playlistInfoCard.show()
        self.statusLabel.setText(f"Downloading {count} videos...")
        self.progressRing.hide()
        
    def onFileStarted(self, index, total, title):
        """Handle file started - create card only when download actually starts"""
        # Clean title to remove unsupported Unicode characters
        clean_title = clean_unicode_text(title) if title else f"Video {index}"
        
        if index not in self.file_cards:
            card = PlaylistFileCard(index, total, clean_title, self)
            card.statusLabel.setText("Downloading...")
            card.statusLabel.setStyleSheet("color: #0078D4;")
            self.file_cards[index] = card
            self.fileCardsLayout.addWidget(card)
            
            # Limit visible cards to prevent UI freeze (show max 10 active cards)
            if len(self.file_cards) > 10:
                # Remove oldest completed/failed cards
                cards_to_remove = []
                for idx, card in list(self.file_cards.items()):
                    if idx < index - 8:  # Keep recent 8 cards
                        cards_to_remove.append(idx)
                        
                for idx in cards_to_remove:
                    if idx in self.file_cards:
                        self.file_cards[idx].deleteLater()
                        del self.file_cards[idx]
        
        # Update status labels with current download info
        self.statusLabel.setText("Downloading")
        
        # Update progress badge with current/total
        if self.downloadProgressBadge:
            self.downloadProgressBadge.setText(f"{index}/{total}")
            self.downloadProgressBadge.show()
        
        self.currentDownloadLabel.setText(f"{clean_title[:60]}...")
        
    def onFileProgress(self, index, progress, speed, eta):
        """Handle file progress"""
        if index in self.file_cards:
            self.file_cards[index].updateProgress(progress, speed, eta)
            
    def onFileCompleted(self, index, file_path, title):
        """Handle file completed"""
        if index in self.file_cards:
            self.file_cards[index].setCompleted()
        
        # Update success badge
        if self.successBadge:
            current = int(self.successBadge.text()) if self.successBadge.text().isdigit() else 0
            self.successBadge.setText(str(current + 1))
            
    def onFileFailed(self, index, error):
        """Handle file failed"""
        if index in self.file_cards:
            self.file_cards[index].setFailed(error)
        
        # Update fail badge
        if self.failBadge:
            current = int(self.failBadge.text()) if self.failBadge.text().isdigit() else 0
            self.failBadge.setText(str(current + 1))
            
    def onPlaylistCompleted(self, success_count, fail_count):
        """Handle playlist completed"""
        self.statusLabel.setText(f"Completed! {success_count} succeeded, {fail_count} failed")
        self.downloadBtn.setEnabled(True)
        self.cancelBtn.hide()
        
        # Update history with final status
        self.updateHistoryComplete(success_count, fail_count)
        
        InfoBar.success(
            title='Playlist Download Complete',
            content=f'{success_count} videos downloaded successfully!',
            parent=self
        )
        
    def addToHistoryStart(self, url):
        """Add playlist to history when starting download"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create initial history entry
        entry = {
            'timestamp': timestamp,
            'status': 'Downloading',
            'title': url,  # Will be updated with actual title
            'path': cfg.get(cfg.downloadFolder),
            'type': 'playlist',
            'items': []
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
        
        # Notify history interface
        self.notifyHistoryUpdate()
        
        return history_index
    
    def updateHistoryComplete(self, success_count, fail_count):
        """Update playlist history when download completes"""
        download_history = cfg.get(cfg.downloadHistory) or []
        
        if 0 <= self.current_history_index < len(download_history):
            # Get playlist title
            playlist_title = self.playlistTitleLabel.text().replace("Playlist: ", "")
            
            # Collect all playlist items from file cards
            items = []
            for index, card in self.file_cards.items():
                item_status = "Success" if card.progressBar.value() == 100 else "Failed"
                items.append({
                    'status': item_status,
                    'title': card.title,
                    'path': ''  # Individual paths not tracked for playlist items
                })
            
            # Update entry
            download_history[self.current_history_index]['title'] = playlist_title
            download_history[self.current_history_index]['status'] = f"Success ({success_count}/{success_count + fail_count})" if success_count > 0 else "Failed"
            download_history[self.current_history_index]['items'] = items
            
            # Save to config
            cfg.set(cfg.downloadHistory, download_history)
            
            # Notify history interface
            self.notifyHistoryUpdate()
    
    def notifyHistoryUpdate(self):
        """Notify history interface to refresh"""
        # Find history interface and refresh it
        main_window = self.window()
        if hasattr(main_window, 'historyInterface'):
            main_window.historyInterface.refreshHistory()
    
    def cancelDownload(self):
        """Cancel download"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.statusLabel.setText("Download cancelled")
            self.downloadBtn.setEnabled(True)
            self.cancelBtn.hide()
            self.progressRing.hide()
            
            # Update history entry to cancelled
            if hasattr(self, 'current_history_index'):
                download_history = cfg.get(cfg.downloadHistory) or []
                if 0 <= self.current_history_index < len(download_history):
                    download_history[self.current_history_index]['status'] = 'Cancelled'
                    cfg.set(cfg.downloadHistory, download_history)
                    self.notifyHistoryUpdate()
