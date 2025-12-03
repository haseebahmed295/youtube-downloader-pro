# coding: utf-8
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QFrame
from qfluentwidgets import (ScrollArea, PushSettingCard, SwitchSettingCard,
                            PrimaryPushButton, BodyLabel, FluentIcon as FIF,
                            setTheme, Theme, InfoBar, ComboBox, LineEdit,
                            CardWidget, CaptionLabel, IconWidget, InfoBarPosition,
                            SubtitleLabel, StrongBodyLabel, HyperlinkButton)

from app.common.config import cfg

class SettingsInterface(ScrollArea):
    """ Settings interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('settingsInterface')

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        # Setting components
        self.themeCombo = ComboBox()
        self.themeCombo.addItems(["Auto", "Light", "Dark"])
        self.themeCombo.setCurrentText(cfg.get(cfg.theme))

        self.downloadFolderCard = PushSettingCard(
            "Change Folder",
            FIF.FOLDER,
            "Download Folder",
            f"Current: {cfg.get(cfg.downloadFolder)}",
            self
        )

        self.qualityCombo = ComboBox()
        self.qualityCombo.addItems(["1080p", "720p", "480p", "360p", "Best Available"])
        self.qualityCombo.setCurrentText(cfg.get(cfg.downloadQuality))

        self.formatCombo = ComboBox()
        self.formatCombo.addItems(["MP4", "WEBM", "3GP"])
        self.formatCombo.setCurrentText(cfg.get(cfg.downloadFormat).upper())

        self.maxDownloadsCombo = ComboBox()
        self.maxDownloadsCombo.addItems(["1", "2", "3", "4", "5", "10"])
        self.maxDownloadsCombo.setCurrentText(str(cfg.get(cfg.maxConcurrentDownloads)))

        self.historyLimitCombo = ComboBox()
        self.historyLimitCombo.addItems(["50", "100", "200", "500", "1000"])
        self.historyLimitCombo.setCurrentText(str(cfg.get(cfg.historyLimit)))

        self.__initWidget()
        self.__initLayout()
        self.__connectSignals()

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

    def __initLayout(self):
        """ Initialize layout """
        # Appearance settings
        self.vBoxLayout.addWidget(self.createSettingGroup(
            "Appearance Settings",
            [self.createComboSetting("Theme", "Change application theme", self.themeCombo, FIF.BRUSH)]
        ))

        # Download settings
        self.vBoxLayout.addWidget(self.createSettingGroup(
            "Download Settings",
            [
                self.downloadFolderCard,
                self.createComboSetting("Default Quality", "Set default video quality", self.qualityCombo, FIF.VIDEO),
                self.createComboSetting("Default Format", "Set default download format", self.formatCombo, FIF.DOCUMENT),
                self.createComboSetting("Max Concurrent Downloads", "Set maximum simultaneous downloads", self.maxDownloadsCombo, FIF.DOWNLOAD)
            ]
        ))

        # History settings
        self.vBoxLayout.addWidget(self.createSettingGroup(
            "History Settings",
            [self.createComboSetting("History Limit", "Set maximum number of history items", self.historyLimitCombo, FIF.HISTORY)]
        ))

        self.vBoxLayout.addStretch()

    def createSettingGroup(self, title, cards):
        """ Create a setting group widget """
        group = CardWidget()
        groupLayout = QVBoxLayout(group)
        groupLayout.setContentsMargins(20, 20, 20, 20)
        groupLayout.setSpacing(15)

        titleLabel = SubtitleLabel(title)
        groupLayout.addWidget(titleLabel)

        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        groupLayout.addWidget(separator)

        # Add cards
        for card in cards:
            groupLayout.addWidget(card)

        return group

    def createComboSetting(self, title, description, combo, icon):
        """ Create a combo box setting card """
        card = QWidget(self)
        cardLayout = QHBoxLayout(card)
        cardLayout.setContentsMargins(10, 10, 10, 10)
        cardLayout.setSpacing(15)

        # Icon
        titleIcon = IconWidget(icon, self)
        titleIcon.setFixedSize(24, 24)
        cardLayout.addWidget(titleIcon)
        
        # Text layout
        textLayout = QVBoxLayout()
        textLayout.setSpacing(4)
        
        titleLabel = StrongBodyLabel(title)
        descLabel = CaptionLabel(description)
        descLabel.setWordWrap(True)
        
        textLayout.addWidget(titleLabel)
        textLayout.addWidget(descLabel)
        cardLayout.addLayout(textLayout, 1)

        # Combo box
        combo.setMinimumWidth(150)
        cardLayout.addWidget(combo)

        return card

    def __connectSignals(self):
        """ Connect signals """
        self.themeCombo.currentTextChanged.connect(self.changeTheme)
        self.downloadFolderCard.clicked.connect(self.changeDownloadFolder)
        self.qualityCombo.currentTextChanged.connect(self.updateQuality)
        self.formatCombo.currentTextChanged.connect(self.updateFormat)
        self.maxDownloadsCombo.currentTextChanged.connect(self.updateMaxDownloads)
        self.historyLimitCombo.currentTextChanged.connect(self.updateHistoryLimit)

    def changeTheme(self, theme):
        """ Change application theme """
        if theme == "Auto":
            setTheme(Theme.AUTO)
        elif theme == "Light":
            setTheme(Theme.LIGHT)
        elif theme == "Dark":
            setTheme(Theme.DARK)

        cfg.set(cfg.theme, theme)
        InfoBar.success(
            title='Success',
            content=f'Theme changed to {theme}',
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def changeDownloadFolder(self):
        """ Change download folder """
        folder = QFileDialog.getExistingDirectory(
            self, "Select Download Folder", cfg.get(cfg.downloadFolder)
        )
        if folder:
            cfg.set(cfg.downloadFolder, folder)
            self.downloadFolderCard.setContent(f"Current: {folder}")
            InfoBar.success(
                title='Success',
                content=f'Download folder changed to {folder}',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def updateQuality(self, quality):
        """ Update default quality """
        cfg.set(cfg.downloadQuality, quality)

    def updateFormat(self, format_type):
        """ Update default format """
        cfg.set(cfg.downloadFormat, format_type.lower())

    def updateMaxDownloads(self, max_downloads):
        """ Update max concurrent downloads """
        cfg.set(cfg.maxConcurrentDownloads, int(max_downloads))

    def updateHistoryLimit(self, history_limit):
        """ Update history limit """
        cfg.set(cfg.historyLimit, int(history_limit))