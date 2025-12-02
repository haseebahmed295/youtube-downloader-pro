# coding: utf-8
import os
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QIODevice

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
    """ Get application icon """
    return QIcon(':/qfluentwidgets/images/logo.png')