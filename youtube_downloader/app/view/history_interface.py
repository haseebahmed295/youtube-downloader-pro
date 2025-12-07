# coding: utf-8
"""
Download History Interface
"""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, 
                               QFrame, QTableWidgetItem, QHeaderView, QApplication, QDialog)
from PySide6.QtGui import QDesktopServices, QColor

from qfluentwidgets import (ScrollArea, PushButton, LineEdit, CardWidget, BodyLabel, 
                            CaptionLabel, FluentIcon as FIF, RoundMenu, Action,
                            InfoBar, InfoBarPosition, SubtitleLabel, TableWidget,
                            IconInfoBadge, InfoBadge, DotInfoBadge, MessageBox)
import os
from datetime import datetime, timedelta

from app.common.config import cfg


class PlaylistDetailsDialog(MessageBox):
    """Dialog to show playlist download details"""
    
    def __init__(self, playlist_items, parent=None):
        super().__init__(
            "Playlist Details",
            f"This playlist contains {len(playlist_items)} items",
            parent
        )
        
        # Create table for playlist items
        self.table = TableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Status', 'Title', 'File Location'])
        
        # Configure table
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.table.setColumnWidth(0, 100)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().hide()
        
        # Add items to table
        for item in playlist_items:
            self.addPlaylistItem(item)
        
        # Add table to dialog
        self.textLayout.addWidget(self.table)
        self.table.setMinimumHeight(400)
        self.table.setMinimumWidth(700)
        
    def addPlaylistItem(self, item):
        """Add playlist item to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Status column with badge
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(8, 0, 8, 0)
        status_layout.setSpacing(8)
        
        status_text = item.get('status', 'Unknown')
        if 'Success' in status_text:
            badge = IconInfoBadge.success(FIF.ACCEPT_MEDIUM)
            status_label = BodyLabel("Success")
            status_label.setStyleSheet("color: #10893E;")
        elif 'Failed' in status_text:
            badge = IconInfoBadge.error(FIF.CANCEL_MEDIUM)
            status_label = BodyLabel("Failed")
            status_label.setStyleSheet("color: #D13438;")
        else:
            badge = DotInfoBadge.info()
            status_label = BodyLabel(status_text)
        
        status_layout.addWidget(badge)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        self.table.setCellWidget(row, 0, status_widget)
        
        # Title column
        title = item.get('title', 'Unknown')
        title_item = QTableWidgetItem(title)
        title_item.setToolTip(title)
        title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
        self.table.setItem(row, 1, title_item)
        
        # Path column
        file_path = item.get('path', '')
        if file_path:
            filename = os.path.basename(file_path)
            path_item = QTableWidgetItem(f"  {filename}")
            path_item.setIcon(FIF.FOLDER.icon())
            path_item.setToolTip(f"Full path: {file_path}")
            path_item.setForeground(QColor(0, 120, 215))
        else:
            path_item = QTableWidgetItem("  N/A")
            path_item.setForeground(QColor(128, 128, 128))
        
        path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
        self.table.setItem(row, 2, path_item)


class HistoryInterface(ScrollArea):
    """ Download history interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('historyInterface')

        # Main widget and layout
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        # History components
        self.historyTable = TableWidget(self)
        self.clearBtn = PushButton("Clear History", self, FIF.DELETE)
        self.exportBtn = PushButton("Export", self, FIF.SAVE)
        self.searchInput = LineEdit()
        self.searchInput.setPlaceholderText("Search history...")

        self.__initWidget()
        self.__initLayout()

        # Connect signals
        self.clearBtn.clicked.connect(self.clearHistory)
        self.exportBtn.clicked.connect(self.exportHistory)
        self.searchInput.textChanged.connect(self.filterHistory)

        # Download history
        self.download_history = []

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

        # Configure history table
        self.historyTable.setObjectName('historyTable')
        self.historyTable.setColumnCount(5)
        self.historyTable.setHorizontalHeaderLabels(['Type', 'Status', 'Date & Time', 'Title', 'File Location'])
        
        # Enable modern TableWidget features
        self.historyTable.setBorderVisible(True)
        self.historyTable.setBorderRadius(8)
        self.historyTable.setWordWrap(False)
        
        # Configure header
        header = self.historyTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setMinimumSectionSize(80)
        
        # Set column widths
        self.historyTable.setColumnWidth(0, 100)  # Type column
        self.historyTable.setColumnWidth(1, 120)  # Status column
        self.historyTable.setColumnWidth(2, 160)  # Time column
        
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
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        historyCardLayout.addWidget(separator)
        
        # History table
        historyCardLayout.addWidget(self.historyTable, 1)
        
        # Add history card to main layout
        self.vBoxLayout.addWidget(historyCard, 1)

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
            self.historyTable.setSpan(0, 0, 1, 5)  # Span across all columns
        else:
            for entry in reversed(self.download_history):  # Show newest first
                self.addHistoryRow(entry)

    def addHistoryRow(self, entry):
        """ Add history row to table """
        row = self.historyTable.rowCount()
        self.historyTable.insertRow(row)

        # Type column with icon
        entry_type = entry.get('type', 'single')
        type_widget = QWidget()
        type_layout = QHBoxLayout(type_widget)
        type_layout.setContentsMargins(8, 0, 8, 0)
        type_layout.setSpacing(8)
        
        if entry_type == 'playlist':
            type_badge = IconInfoBadge.attension(FIF.LIBRARY)
            type_label = BodyLabel("Playlist")
        else:
            type_badge = IconInfoBadge.info(FIF.VIDEO)
            type_label = BodyLabel("Single")
        
        type_layout.addWidget(type_badge)
        type_layout.addWidget(type_label)
        type_layout.addStretch()
        
        self.historyTable.setCellWidget(row, 0, type_widget)

        # Status column with badges
        status_text = entry['status']
        
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
        elif 'Downloading' in status_text:
            badge = DotInfoBadge.attension()
            status_label = BodyLabel("Downloading")
            status_label.setStyleSheet("color: #0078D4;")
        elif 'Cancelled' in status_text:
            badge = IconInfoBadge.warning(FIF.CANCEL)
            badge.setToolTip("Download was cancelled by user")
            status_label = BodyLabel("Cancelled")
            status_label.setStyleSheet("color: #F7630C;")
        elif 'Interrupted' in status_text:
            badge = IconInfoBadge.warning(FIF.SYNC)
            badge.setToolTip("Download was interrupted (app closed)")
            status_label = BodyLabel("Interrupted")
            status_label.setStyleSheet("color: #CA5010;")
        else:
            badge = DotInfoBadge.info()
            status_label = BodyLabel(status_text)
        
        status_layout.addWidget(badge)
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        self.historyTable.setCellWidget(row, 1, status_widget)

        # Time column
        timestamp = entry['timestamp']
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            today = datetime.now().date()
            
            if dt.date() == today:
                time_display = f"Today {dt.strftime('%H:%M:%S')}"
            elif dt.date() == today - timedelta(days=1):
                time_display = f"Yesterday {dt.strftime('%H:%M:%S')}"
            else:
                time_display = dt.strftime('%Y-%m-%d %H:%M')
        except:
            time_display = timestamp
            
        time_item = QTableWidgetItem(time_display)
        time_item.setToolTip(f"Downloaded on {timestamp}")
        time_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
        self.historyTable.setItem(row, 2, time_item)

        # Title column
        title_text = entry.get('title', entry.get('details', 'Unknown'))
        
        # For playlists, show item count if available
        if entry_type == 'playlist' and 'items' in entry:
            item_count = len(entry['items'])
            title_text = f"{title_text} ({item_count} items)"
        
        title_item = QTableWidgetItem(title_text)
        title_item.setToolTip(title_text)
        title_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
        self.historyTable.setItem(row, 3, title_item)
        
        # Path column
        file_path = entry.get('path', '')
        if file_path:
            filename = os.path.basename(file_path)
            path_item = QTableWidgetItem(f"  {filename}")
            path_item.setIcon(FIF.FOLDER.icon())
            path_item.setToolTip(f"Full path: {file_path}\nDouble-click to open")
            path_item.setForeground(QColor(0, 120, 215))
        else:
            path_item = QTableWidgetItem("  N/A")
            path_item.setForeground(QColor(128, 128, 128))
            path_item.setToolTip("File path not available")
            
        path_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
        self.historyTable.setItem(row, 4, path_item)

    def clearHistory(self):
        """ Clear history """
        confirm = MessageBox(
            "Clear History",
            "Are you sure you want to clear all download history?",
            self
        )
        if confirm.exec():
            self.historyTable.setRowCount(0)
            self.download_history.clear()
            cfg.set(cfg.downloadHistory, [])
            InfoBar.success(
                title='History Cleared',
                content='Download history has been cleared',
                parent=self
            )

    def loadHistory(self):
        """ Load history from config """
        try:
            stored_history = cfg.get(cfg.downloadHistory)
            if isinstance(stored_history, list):
                self.download_history = stored_history
                self.updateHistoryDisplay()
        except:
            self.download_history = []
    
    def refreshHistory(self):
        """ Refresh history display from config """
        self.loadHistory()
    
    def updateHistoryEntry(self, index, status, path=None):
        """ Update a specific history entry """
        if 0 <= index < len(self.download_history):
            self.download_history[index]['status'] = status
            if path:
                self.download_history[index]['path'] = path
            cfg.set(cfg.downloadHistory, self.download_history)
            self.updateHistoryDisplay()

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
                        f.write("Type,Status,Time,Title,Path\n")
                        for entry in self.download_history:
                            f.write(f'"{entry.get("type", "single")}","{entry["status"]}","{entry["timestamp"]}","{entry.get("title", "")}","{entry.get("path", "")}"\n')
                    else:
                        for entry in self.download_history:
                            f.write(f"{entry.get('type', 'single')} | {entry['status']} | {entry['timestamp']} | {entry.get('title', '')} | {entry.get('path', '')}\n")
                
                InfoBar.success(
                    title='Exported',
                    content=f'History exported to {file_path}',
                    parent=self
                )
            except Exception as e:
                InfoBar.error(
                    title='Export Failed',
                    content=f"Failed to export history: {str(e)}",
                    parent=self
                )
    
    def showHistoryContextMenu(self, pos):
        """ Show context menu for history table """
        item = self.historyTable.itemAt(pos)
        if item:
            row = item.row()
            
            # Get entry type and data
            entry = self.download_history[len(self.download_history) - 1 - row] if row < len(self.download_history) else None
            
            menu = RoundMenu(parent=self)
            
            # For playlist entries, add option to view details
            if entry and entry.get('type') == 'playlist' and 'items' in entry:
                viewDetailsAction = Action(FIF.INFO, "View Playlist Details")
                viewDetailsAction.triggered.connect(lambda: self.showPlaylistDetails(entry))
                menu.addAction(viewDetailsAction)
                menu.addSeparator()
            
            path_item = self.historyTable.item(row, 4)
            if path_item and path_item.text().strip() and path_item.text() != "N/A":
                file_path = entry.get('path', '') if entry else ''
                
                if file_path and os.path.exists(file_path):
                    openFileAction = Action(FIF.DOCUMENT, "Open File")
                    openFileAction.triggered.connect(lambda: self.openFile(file_path))
                    menu.addAction(openFileAction)
                    
                    openFolderAction = Action(FIF.FOLDER, "Open Folder")
                    openFolderAction.triggered.connect(lambda: self.openFolder(file_path))
                    menu.addAction(openFolderAction)
                    
                    copyPathAction = Action(FIF.COPY, "Copy Path")
                    copyPathAction.triggered.connect(lambda: QApplication.clipboard().setText(file_path))
                    menu.addAction(copyPathAction)
            
            if menu.actions():
                menu.exec(self.historyTable.mapToGlobal(pos))
    
    def showPlaylistDetails(self, entry):
        """Show playlist details dialog"""
        items = entry.get('items', [])
        dialog = PlaylistDetailsDialog(items, self)
        dialog.exec()
    
    def openHistoryFile(self, index):
        """ Open file from history on double click """
        row = index.row()
        entry = self.download_history[len(self.download_history) - 1 - row] if row < len(self.download_history) else None
        
        if entry:
            # If it's a playlist, show details
            if entry.get('type') == 'playlist' and 'items' in entry:
                self.showPlaylistDetails(entry)
            else:
                # If it's a single download, open the file
                file_path = entry.get('path', '')
                if file_path:
                    self.openFile(file_path)
    
    def openFile(self, file_path):
        """ Open file """
        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        else:
            InfoBar.error(
                title='File Not Found',
                content="The file no longer exists at this location",
                parent=self
            )
    
    def openFolder(self, file_path):
        """ Open folder containing file """
        if os.path.exists(file_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(file_path)))
        else:
            InfoBar.error(
                title='Folder Not Found',
                content="The folder no longer exists",
                parent=self
            )
