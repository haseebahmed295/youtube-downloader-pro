# coding: utf-8
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import (ScrollArea, BodyLabel, HyperlinkLabel, PrimaryPushButton,
                            CardWidget, CaptionLabel, FluentIcon as FIF, SubtitleLabel,
                            StrongBodyLabel, TitleLabel, IconWidget)

class AboutInterface(ScrollArea):
    """ About interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('aboutInterface')

        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ Initialize widgets """
        self.view.setObjectName('view')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.enableTransparentBackground()

        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def __initLayout(self):
        """ Initialize layout """
        # Header card
        headerCard = CardWidget(self)
        headerLayout = QVBoxLayout(headerCard)
        headerLayout.setContentsMargins(30, 30, 30, 30)
        headerLayout.setSpacing(15)
        headerLayout.setAlignment(Qt.AlignCenter)
        
        appIcon = IconWidget(FIF.VIDEO, self)
        appIcon.setFixedSize(64, 64)
        headerLayout.addWidget(appIcon, 0, Qt.AlignCenter)
        
        appTitle = TitleLabel("Ytp Downloader")
        appTitle.setAlignment(Qt.AlignCenter)
        headerLayout.addWidget(appTitle)
        
        appVersion = CaptionLabel("Version 1.0.0")
        appVersion.setAlignment(Qt.AlignCenter)
        headerLayout.addWidget(appVersion)
        
        appDesc = BodyLabel("A modern YouTube video and audio downloader\nbuilt with PySide6-Fluent-Widgets")
        appDesc.setAlignment(Qt.AlignCenter)
        appDesc.setWordWrap(True)
        headerLayout.addWidget(appDesc)

        # Features
        features = self.createInfoCard(
            "Features",
            """• Download YouTube videos and playlists
• Multiple quality options (Best, 1080p, 720p, 480p, 360p)
• Audio-only download with MP3, AAC, OGG, WAV formats
• Video formats: MP4, WEBM, 3GP
• Real-time download progress with speed and ETA
• Download history with search and export
• Context menu for quick file access
• Keyboard shortcuts (Ctrl+Enter to download, Esc to cancel)
• Modern Fluent UI design with dark/light theme support""",
            FIF.CHECKBOX
        )

        # Technologies
        technologies = self.createInfoCard(
            "Technologies",
            """• PySide6 - Qt for Python framework
• PySide6-Fluent-Widgets - Modern Fluent Design UI components
• yt-dlp - Powerful YouTube downloading library
• Python 3.8+ - Modern Python features""",
            FIF.CODE
        )

        # Links card
        linksCard = CardWidget(self)
        linksLayout = QVBoxLayout(linksCard)
        linksLayout.setContentsMargins(20, 20, 20, 20)
        linksLayout.setSpacing(15)
        
        linksTitle = SubtitleLabel("Links & Resources")
        linksLayout.addWidget(linksTitle)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        linksLayout.addWidget(separator)
        
        githubBtn = PrimaryPushButton(FIF.GITHUB, "GitHub Repository")
        githubBtn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/haseebahmed295/youtube-downloader-pro")))
        
        linksLayout.addWidget(githubBtn)

        # Add to main layout
        self.vBoxLayout.addWidget(headerCard)
        self.vBoxLayout.addWidget(features)
        self.vBoxLayout.addWidget(technologies)
        self.vBoxLayout.addWidget(linksCard)
        self.vBoxLayout.addStretch()

    def createInfoCard(self, title, content, icon):
        """ Create an information card """
        card = CardWidget(self)
        cardLayout = QVBoxLayout(card)
        cardLayout.setContentsMargins(20, 20, 20, 20)
        cardLayout.setSpacing(15)

        # Title with icon
        titleLayout = QHBoxLayout()
        titleIcon = IconWidget(icon, self)
        titleIcon.setFixedSize(24, 24)
        titleLabel = SubtitleLabel(title)

        titleLayout.addWidget(titleIcon)
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")

        # Content
        contentLabel = BodyLabel(content)
        contentLabel.setWordWrap(True)

        cardLayout.addLayout(titleLayout)
        cardLayout.addWidget(separator)
        cardLayout.addWidget(contentLabel)

        return card