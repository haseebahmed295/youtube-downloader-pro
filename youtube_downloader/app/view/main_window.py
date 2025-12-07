# coding: utf-8
import time
from typing import List
from PySide6.QtCore import Qt, Signal, QEasingCurve, QUrl, QSize, QTimer
from PySide6.QtGui import QIcon, QDesktopServices, QColor
from PySide6.QtWidgets import QApplication, QHBoxLayout, QFrame, QWidget

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen, SystemThemeListener, isDarkTheme, FluentIcon as FIF)
from qfluentwidgets import setTheme, Theme

from app.common.config import cfg
from app.resource.resource import getAppIcon
from app.view.download_history_interface import DownloadHistoryInterface
from app.view.playlist_interface import PlaylistInterface
from app.view.settings_interface import SettingsInterface
from app.view.about_interface import AboutInterface

class MainWindow(FluentWindow):
    """ Main window """

    def __init__(self):
        super().__init__()
        self.initWindow()
        # create system theme listener
        self.themeListener = SystemThemeListener(self)

        # set initial theme from config before creating interfaces
        self.setInitialTheme()

        # create sub interfaces
        self.downloadHistoryInterface = DownloadHistoryInterface(self)
        self.playlistInterface = PlaylistInterface(self)
        self.settingsInterface = SettingsInterface(self)
        self.aboutInterface = AboutInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

        # start theme listener
        self.themeListener.start()

    def connectSignalToSlot(self):
        pass

    def setInitialTheme(self):
        """ Set initial theme from config """
        theme = cfg.get(cfg.theme)
        if theme == "Auto":
            setTheme(Theme.AUTO)
        elif theme == "Light":
            setTheme(Theme.LIGHT)
        elif theme == "Dark":
            setTheme(Theme.DARK)

    def initNavigation(self):
        """ Initialize navigation items """
        # add navigation items
        self.addSubInterface(self.downloadHistoryInterface, FIF.DOWNLOAD, "Download & History")
        self.addSubInterface(self.playlistInterface, FIF.MENU, "Playlist Download")
        self.addSubInterface(self.settingsInterface, FIF.SETTING, "Settings")
        self.addSubInterface(self.aboutInterface, FIF.INFO, "About")

        # add custom widget to bottom
        self.navigationInterface.addItem(
            routeKey='github',
            icon=FIF.GITHUB,
            text="GitHub",
            onClick=self.onGitHub,
            selectable=False,
            tooltip="View on GitHub",
            position=NavigationItemPosition.BOTTOM
        )

    def initWindow(self):
        """ Initialize window """
        self.resize(1000, 800)
        self.setMinimumWidth(800)
        self.setWindowIcon(getAppIcon())
        self.setWindowTitle('YouTube Downloader')

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(200, 200))  # Increased from 106x106
        self.splashScreen.raise_()

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onGitHub(self):
        """ Open GitHub page """
        QDesktopServices.openUrl(QUrl("https://github.com/zhiyiYo/PyQt-Fluent-Widgets"))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # retry
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))