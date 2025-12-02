#!/usr/bin/env python3
# coding:utf-8

"""
YouTube Downloader Application
Main entry point for the application
"""

import os
import sys
from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from qfluentwidgets import FluentTranslator
from app.common.config import cfg
from app.view.main_window import MainWindow

def main():
    # Enable DPI scaling
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    # Create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    # Internationalization
    from PySide6.QtCore import QLocale
    locale_str = cfg.get(cfg.language)
    locale = QLocale(locale_str) if locale_str else QLocale()
    translator = FluentTranslator(locale)
    appTranslator = QTranslator()
    appTranslator.load(locale, "youtube_downloader", ".", ":/i18n")

    app.installTranslator(translator)
    app.installTranslator(appTranslator)

    # Create main window
    w = MainWindow()
    w.show()

    app.exec()

if __name__ == "__main__":
    main()