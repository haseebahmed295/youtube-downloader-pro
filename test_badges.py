# coding:utf-8
import sys
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from qfluentwidgets import (InfoBadge, IconInfoBadge, setTheme, Theme, DotInfoBadge, 
                            ToolButton, InfoBadgePosition, InfoBadgeManager, 
                            SubtitleLabel, BodyLabel)
from qfluentwidgets import FluentIcon as FIF


@InfoBadgeManager.register('Custom')
class CustomInfoBadgeManager(InfoBadgeManager):
    """Custom info badge manager"""
    
    def position(self):
        pos = self.target.geometry().center()
        x = pos.x() - self.badge.width() // 2
        y = self.target.y() - self.badge.height() // 2
        return QPoint(x, y)


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        # setTheme(Theme.DARK)
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        titleLabel = SubtitleLabel("InfoBadge Showcase")
        self.vBoxLayout.addWidget(titleLabel)
        
        # Info badges section
        self.addSection("Number Badges", self.createNumberBadges())
        
        # Dot info badges section
        self.addSection("Status Indicators", self.createDotBadges())
        
        # Icon info badges section
        self.addSection("Icon Badges", self.createIconBadges())
        
        # Button with badge example
        buttonLabel = BodyLabel("Badge on Button:")
        self.vBoxLayout.addWidget(buttonLabel)
        
        self.button = ToolButton(FIF.BASKETBALL, self)
        self.button.setIconSize(QSize(24, 24))
        self.button.setFixedSize(48, 48)
        self.vBoxLayout.addWidget(self.button, 0, Qt.AlignLeft)
        
        InfoBadge.success(5, self, target=self.button, position=InfoBadgePosition.TOP_RIGHT)
        
        self.vBoxLayout.addStretch(1)
        self.resize(600, 500)
        self.setWindowTitle('InfoBadge Demo')
    
    def addSection(self, title, layout):
        """Add a section with title and content"""
        label = BodyLabel(title)
        self.vBoxLayout.addWidget(label)
        self.vBoxLayout.addLayout(layout)
    
    def createNumberBadges(self):
        """Create number badges layout"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addStretch(1)
        layout.addWidget(InfoBadge.info(1))
        layout.addWidget(InfoBadge.success(10))
        layout.addWidget(InfoBadge.attension(100))
        layout.addWidget(InfoBadge.warning(1000))
        layout.addWidget(InfoBadge.error(10000))
        layout.addWidget(InfoBadge.custom('1w+', '#005fb8', '#60cdff'))
        layout.addStretch(1)
        return layout
    
    def createDotBadges(self):
        """Create dot badges layout"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addStretch(1)
        layout.addWidget(DotInfoBadge.info())
        layout.addWidget(DotInfoBadge.success())
        layout.addWidget(DotInfoBadge.attension())
        layout.addWidget(DotInfoBadge.warning())
        layout.addWidget(DotInfoBadge.error())
        layout.addWidget(DotInfoBadge.custom('#005fb8', '#60cdff'))
        layout.addStretch(1)
        return layout
    
    def createIconBadges(self):
        """Create icon badges layout"""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addStretch(1)
        layout.addWidget(IconInfoBadge.info(FIF.ACCEPT_MEDIUM))
        layout.addWidget(IconInfoBadge.success(FIF.ACCEPT_MEDIUM))
        layout.addWidget(IconInfoBadge.attension(FIF.ACCEPT_MEDIUM))
        layout.addWidget(IconInfoBadge.warning(FIF.CANCEL_MEDIUM))
        layout.addWidget(IconInfoBadge.error(FIF.CANCEL_MEDIUM))
        
        badge = IconInfoBadge.custom(FIF.RINGER, '#005fb8', '#60cdff')
        badge.setFixedSize(32, 32)
        badge.setIconSize(QSize(16, 16))
        layout.addWidget(badge)
        
        layout.addStretch(1)
        return layout


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()
