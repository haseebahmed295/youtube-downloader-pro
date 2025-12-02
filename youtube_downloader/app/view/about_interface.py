# coding: utf-8
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import (ScrollArea, BodyLabel, HyperlinkLabel, PrimaryPushButton,
                            CardWidget, CaptionLabel, FluentIcon as FIF)

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
        # App info
        appInfo = self.createInfoCard(
            "YouTube Downloader",
            "A modern YouTube video and audio downloader built with PySide6-Fluent-Widgets",
            FIF.INFO
        )

        # Features
        features = self.createInfoCard(
            "Features",
            """• Download YouTube videos and playlists
• Multiple quality options (1080p, 720p, 480p, 360p)
• Audio-only download support
• Multiple format options (MP4, WEBM, 3GP, MP3, AAC)
• Download history tracking
• Concurrent downloads
• Modern Fluent UI design
• Dark/Light theme support""",
            FIF.INFO
        )

        # Technologies
        technologies = self.createInfoCard(
            "Technologies",
            """• PySide6 - Qt for Python
• PySide6-Fluent-Widgets - Modern UI components
• PyTube - YouTube downloading library
• MoviePy - Video processing (future enhancement)""",
            FIF.CODE
        )

        # Links
        linksLayout = QHBoxLayout()
        linksLayout.setSpacing(20)

        githubBtn = PrimaryPushButton(FIF.GITHUB, "GitHub")
        githubBtn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/zhiyiYo/PyQt-Fluent-Widgets")))

        docsBtn = PrimaryPushButton(FIF.DOCUMENT, "Documentation")
        docsBtn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://qfluentwidgets.com")))

        linksLayout.addWidget(githubBtn)
        linksLayout.addWidget(docsBtn)
        linksLayout.addStretch()

        # Add to main layout
        self.vBoxLayout.addWidget(appInfo)
        self.vBoxLayout.addWidget(features)
        self.vBoxLayout.addWidget(technologies)
        self.vBoxLayout.addLayout(linksLayout)
        self.vBoxLayout.addStretch()

    def createInfoCard(self, title, content, icon):
        """ Create an information card """
        card = CardWidget(self)
        cardLayout = QVBoxLayout(card)
        cardLayout.setContentsMargins(20, 20, 20, 20)
        cardLayout.setSpacing(15)

        # Title with icon
        titleLayout = QHBoxLayout()
        titleIcon = QLabel()
        titleIcon.setPixmap(icon.icon().pixmap(24, 24))
        titleLabel = BodyLabel(title)
        titleLabel.setStyleSheet("font-size: 18px; font-weight: bold;")

        titleLayout.addWidget(titleIcon)
        titleLayout.addWidget(titleLabel)
        titleLayout.addStretch()

        # Content
        contentLabel = BodyLabel(content)
        contentLabel.setWordWrap(True)

        cardLayout.addLayout(titleLayout)
        cardLayout.addWidget(contentLabel)

        return card