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
from app.common.logger import setup_logger, get_logger
from app.view.main_window import MainWindow
from app.resource.resource import getAppIcon

def main():
    # Set up logging first
    logger = setup_logger(level='DEBUG')  # Change to 'DEBUG' for more verbose logging
    logger.info("Initializing YouTube Downloader...")
    
    try:
        # Enable DPI scaling
        if cfg.get(cfg.dpiScale) != "Auto":
            os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
            os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))
            logger.debug(f"DPI Scale set to: {cfg.get(cfg.dpiScale)}")

        # Create application
        logger.info("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        
        # Set application icon for taskbar (Windows)
        app.setWindowIcon(getAppIcon())
        
        # Set AppUserModelID for Windows taskbar icon
        if sys.platform == 'win32':
            try:
                import ctypes
                myappid = 'com.youtubedownloader.app.1.0'  # arbitrary string
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                logger.debug("Windows AppUserModelID set for taskbar icon")
            except Exception as e:
                logger.warning(f"Could not set AppUserModelID: {e}")

        # Internationalization
        from PySide6.QtCore import QLocale
        locale_str = cfg.get(cfg.language)
        locale = QLocale(locale_str) if locale_str else QLocale()
        translator = FluentTranslator(locale)
        appTranslator = QTranslator()
        appTranslator.load(locale, "youtube_downloader", ".", ":/i18n")

        app.installTranslator(translator)
        app.installTranslator(appTranslator)
        logger.info(f"Language set to: {locale_str or 'system default'}")

        # Create main window
        logger.info("Creating main window...")
        w = MainWindow()
        w.show()
        logger.info("Application started successfully")

        # Run application
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.critical(f"Fatal error during startup: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())