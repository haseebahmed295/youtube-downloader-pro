# coding: utf-8
"""
Combined Download and History Interface
"""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFileDialog, QFrame, QTableWidgetItem, 
                               QHeaderView, QApplication)
from PySide6.QtGui import QDesktopServices, QColor, QKeySequence, QShortcut

from qfluentwidgets import (ScrollArea, PushButton, LineEdit, ComboBox, SwitchButton,
                            ProgressBar, InfoBar, InfoBarPosition, InfoBarIcon,
                            CardWidget, BodyLabel, CaptionLabel, PrimaryPushButton,
                            FluentIcon as FIF, RoundMenu, Action,
                            IndeterminateProgressRing, MessageBox,
                            StrongBodyLabel, SubtitleLabel, TableWidget,
                            IconInfoBadge, InfoBadge, DotInfoBadge)
import os
from datetime import datetime, timedelta

from app.common.config import cfg
from app.components.download_worker import DownloadWorker

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

        # History components
        self.historyTable = TableWidget(self)
        self.clearBtn = PushButton("Clear History", self, FIF.DELETE)
        self.exportBtn = PushButton("Export", self, FIF.SAVE)
        self.searchInput = LineEdit()
        self.searchInput.setPlaceholderText("Search history...")

        self.__initWidget()
        self.__initLayout()

        # Connect signals
        self.downloadBtn.clicked.connect(self.startDownload)
        self.cancelBtn.clicked.connect(self.cancelDownload)
        self.audioOnlySwitch.checkedChanged.connect(self.updateFormatOptions)
        self.clearBtn.clicked.connect(self.clearHistory)
        self.exportBtn.clicked.connect(self.exportHistory)
        self.searchInput.textChanged.connect(self.filterHistory)
        
        # Keyboard shortcuts
        self.downloadShortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.downloadShortcut.activated.connect(self.startDownload)
        self.cancelShortcut = QShortcut(QKeySequence("Escape"), self)
        self.cancelShortcut.activated.connect(self.cancelDownload)

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
        self.urlInput.setPlaceholderText("Enter YouTube URL here (Ctrl+Enter to download)...")
        self.urlInput.setClearButtonEnabled(True)
        self.urlInput.setMinimumHeight(40)

        # Configure quality combo
        self.qualityCombo.addItems(["Best Available", "1080p", "720p", "480p", "360p"])
        self.qualityCombo.setCurrentText(cfg.get(cfg.downloadQuality))
        self.qualityCombo.setMinimumWidth(150)

        # Configure format combo
        self.formatCombo.addItems(["MP4", "WEBM", "3GP"])
        self.formatCombo.setCurrentText(cfg.get(cfg.downloadFormat).upper())
        self.formatCombo.setMinimumWidth(120)

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

        # Configure history table with improved styling (using TableWidget)
        self.historyTable.setObjectName('historyTable')
        self.historyTable.setColumnCount(4)
        self.historyTable.setHorizontalHeaderLabels(['Status', 'Date & Time', 'Video Title', 'File Location'])
        
        # Enable modern TableWidget features
        self.historyTable.setBorderVisible(True)
        self.historyTable.setBorderRadius(8)
        self.historyTable.setWordWrap(False)
        
        # Configure header
        header = self.historyTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setMinimumSectionSize(80)
        
        # Set column widths
        self.historyTable.setColumnWidth(0, 120)  # Status column
        self.historyTable.setColumnWidth(1, 160)  # Time column
        
        # Row height
        self.historyTable.verticalHeader().setDefaultSectionSize(40)
        self.historyTable.verticalHeader().hide()
        
        # Context menu and interactions
        self.historyTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.historyTable.customContextMenuRequested.connect(self.showHistoryContextMenu)
        self.historyTable.doubleClicked.connect(self.openHistoryFile)
        
        # Configure search input
        self.searchInput.setClearButtonEnabled(True)
        self.searchInput.setMinimumWidth(250)
        self.searchInput.setFixedHeight(32)

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

        # History section
        historyCard = CardWidget(self)
        historyCardLayout = QVBoxLayout(historyCard)
        historyCardLayout.setContentsMargins(20, 20, 20, 20)
        historyCardLayout.setSpacing(15)
        
        # History title row
        historyTitleRow = QHBoxLayout()
        historyTitle = SubtitleLabel("Download History")
        historyTitleRow.addWidget(historyTitle)
        historyTitleRow.addStretch()
        historyTitleRow.addWidget(self.searchInput)
        historyTitleRow.addWidget(self.exportBtn)
        historyTitleRow.addWidget(self.clearBtn)
        historyCardLayout.addLayout(historyTitleRow)
        
        # Separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        historyCardLayout.addWidget(separator2)
        
        # History table
        historyCardLayout.addWidget(self.historyTable, 1)
        
        # Add history card to main layout
        self.vBoxLayout.addWidget(historyCard, 1)

        # Add info bar for instructions
        self.addInfoBar()

    def addInfoBar(self):
        """ Add information bar with instructions """
        infoBar = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="Welcome to Ytp Downloader",
            content="Enter a YouTube video or playlist URL and press Ctrl+Enter or click Download. "
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

        # Add to history
        self.addToHistory(title, "Success", file_path)

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

        # Add to history
        self.addToHistory(error_message, "Failed", "")

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
        """ Add entry to download history """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create history entry
        entry = {
            'timestamp': timestamp,
            'status': status,
            'title': title,
            'path': file_path
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
        
        if not self.download_history:
            # Show empty state message
            self.historyTable.setRowCount(1)
            empty_item = QTableWidgetItem("No download history yet. Start downloading videos to see them here!")
            empty_item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            empty_item.setForeground(QColor(128, 128, 128))
            font = empty_item.font()
            font.setItalic(True)
            empty_item.setFont(font)
            self.historyTable.setItem(0, 0, empty_item)
            self.historyTable.setSpan(0, 0, 1, 4)  # Span across all columns
        else:
            for entry in reversed(self.download_history):  # Show newest first
                self.addHistoryRow(entry)

    def addHistoryRow(self, entry):
        """ Add history row to table with improved formatting using badges """
        row = self.historyTable.rowCount()
        self.historyTable.insertRow(row)

        # Status column with badges instead of text
        status_text = entry['status']
        
        # Create a widget to hold the badge
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(8, 0, 8, 0)
        status_layout.setSpacing(8)
        
        if 'Success' in status_text:
            badge = IconInfoBadge.success(FIF.ACCEPT_MEDIUM)
            badge.setToolTip("Download completed successfully")
            status_label = BodyLabel("Success")
            status_label.setStyleSheet("color: #10893E;")
        elif 'Failed' in status_text:
            badge = IconInfoBadge.error(FIF.CANCEL_MEDIUM)
            error_msg = entry.get('title', 'Download failed')
            badge.setToolTip(f"Error: {error_msg}")
            status_label = BodyLabel("Failed")
            status_label.setStyleSheet("color: #D13438;")
        else:
            badge = DotInfoBadge.info()
            status_label = BodyLabel(status_text)
        
        status_layout.addWidget(badge)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        self.historyTable.setCellWidget(row, 0, status_widget)

        # Time column with better formatting
        timestamp = entry['timestamp']
        try:
            # Parse and reformat timestamp for better display
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            today = datetime.now().date()
            
            if dt.date() == today:
                # Show "Today" for today's downloads
                time_display = f"Today {dt.strftime('%H:%M:%S')}"
            elif dt.date() == today - timedelta(days=1):
                # Show "Yesterday" for yesterday's downloads
                time_display = f"Yesterday {dt.strftime('%H:%M:%S')}"
            else:
                # Show full date for older downloads
                time_display = dt.strftime('%Y-%m-%d %H:%M')
        except:
            time_display = timestamp
            
        time_item = QTableWidgetItem(time_display)
        time_item.setToolTip(f"Downloaded on {timestamp}")
        time_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.historyTable.setItem(row, 1, time_item)

        # Title column with truncation and tooltip
        title_text = entry.get('title', entry.get('details', 'Unknown'))
        title_item = QTableWidgetItem(title_text)
        title_item.setToolTip(title_text)  # Full title on hover
        title_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Make title bold for successful downloads
        if 'Success' in status_text:
            font = title_item.font()
            font.setBold(False)  # Keep normal weight for readability
            title_item.setFont(font)
        
        self.historyTable.setItem(row, 2, title_item)
        
        # Path column with folder icon and shortened display
        file_path = entry.get('path', '')
        if file_path:
            # Show just filename, not full path
            filename = os.path.basename(file_path)
            path_item = QTableWidgetItem(f"  {filename}")
            path_item.setIcon(FIF.FOLDER.icon())
            path_item.setToolTip(f"Full path: {file_path}\nDouble-click to open")
            path_item.setForeground(QColor(0, 120, 215))  # Blue for clickable items
        else:
            path_item = QTableWidgetItem("  N/A")
            path_item.setForeground(QColor(128, 128, 128))  # Gray for N/A
            path_item.setToolTip("File path not available")
            
        path_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.historyTable.setItem(row, 3, path_item)

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
    
    def filterHistory(self, text):
        """ Filter history based on search text """
        for row in range(self.historyTable.rowCount()):
            should_show = False
            for col in range(self.historyTable.columnCount()):
                item = self.historyTable.item(row, col)
                if item and text.lower() in item.text().lower():
                    should_show = True
                    break
            self.historyTable.setRowHidden(row, not should_show)
    
    def exportHistory(self):
        """ Export history to file """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "download_history.txt", "Text Files (*.txt);;CSV Files (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if file_path.endswith('.csv'):
                        f.write("Status,Time,Title,Path\n")
                        for entry in self.download_history:
                            f.write(f'"{entry["status"]}","{entry["timestamp"]}","{entry.get("title", "")}","{entry.get("path", "")}"\n')
                    else:
                        for entry in self.download_history:
                            f.write(f"{entry['status']} | {entry['timestamp']} | {entry.get('title', '')} | {entry.get('path', '')}\n")
                
                InfoBar.success(
                    title='Exported',
                    content=f'History exported to {file_path}',
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=3000,
                    parent=self
                )
            except Exception as e:
                self.showError(f"Failed to export history: {str(e)}")
    
    def showHistoryContextMenu(self, pos):
        """ Show context menu for history table """
        item = self.historyTable.itemAt(pos)
        if item:
            row = item.row()
            path_item = self.historyTable.item(row, 3)
            if path_item and path_item.text():
                menu = RoundMenu(parent=self)
                
                openFileAction = Action(FIF.DOCUMENT, "Open File")
                openFileAction.triggered.connect(lambda: self.openFile(path_item.text()))
                menu.addAction(openFileAction)
                
                openFolderAction = Action(FIF.FOLDER, "Open Folder")
                openFolderAction.triggered.connect(lambda: self.openFolder(path_item.text()))
                menu.addAction(openFolderAction)
                
                copyPathAction = Action(FIF.COPY, "Copy Path")
                copyPathAction.triggered.connect(lambda: QApplication.clipboard().setText(path_item.text()))
                menu.addAction(copyPathAction)
                
                menu.exec(self.historyTable.mapToGlobal(pos))
    
    def openHistoryFile(self, index):
        """ Open file from history on double click """
        path_item = self.historyTable.item(index.row(), 3)
        if path_item and path_item.text():
            self.openFile(path_item.text())
    
    def openFile(self, file_path):
        """ Open file """
        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            self.showError("File not found")
    
    def openFolder(self, file_path):
        """ Open folder containing file """
        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))
        else:
            self.showError("Folder not found")