# coding: utf-8
import os
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QFile, QIODevice, Qt

def getIcon(icon_name):
    """ Get icon from resources """
    # In a real app, this would load from a resource file
    # For now, we'll use the built-in Fluent icons
    from qfluentwidgets import FluentIcon as FIF
    return getattr(FIF, icon_name, FIF.INFO)

def loadStyleSheet(file_name):
    """ Load stylesheet from file """
    path = os.path.join(os.path.dirname(__file__), 'qss', file_name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def getAppIcon():
    """ Get application icon with multiple sizes for better display """
    # Load from local file system
    icon_path = os.path.join(os.path.dirname(__file__), 'images', 'logo.png')
    if os.path.exists(icon_path):
        icon = QIcon()
        # Add multiple sizes for better scaling on different displays
        pixmap = QPixmap(icon_path)
        icon.addPixmap(pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.addPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.addPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.addPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.addPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.addPixmap(pixmap.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon.addPixmap(pixmap)  # Original size
        return icon
    return QIcon(':/qfluentwidgets/images/logo.png')