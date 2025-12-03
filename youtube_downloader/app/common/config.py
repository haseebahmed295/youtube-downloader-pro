# coding:utf-8
import os
import json
from enum import Enum
from PySide6.QtCore import QStandardPaths

class ConfigItem:
    """ Configuration item """

    def __init__(self, group: str, name: str, defaultValue, validator=None):
        self.group = group
        self.name = name
        self.defaultValue = defaultValue
        self.validator = validator

    def __str__(self):
        return f"{self.group}/{self.name}"

class Config:
    """ Configuration manager """

    def __init__(self):
        self._config = {}
        self._items = []
        self._file = os.path.join(self._getConfigDir(), "config.json")

        # load config from file
        self._load()

    def _getConfigDir(self):
        """ get config directory """
        config_dir = os.path.join(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation), "YouTubeDownloader")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    def _load(self):
        """ load config from file """
        if not os.path.exists(self._file):
            return

        try:
            with open(self._file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")

    def _save(self):
        """ save config to file """
        try:
            with open(self._file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def addItem(self, item: ConfigItem):
        """ add config item """
        self._items.append(item)

        # set default value if not exists
        if item.group not in self._config:
            self._config[item.group] = {}

        if item.name not in self._config[item.group]:
            self._config[item.group][item.name] = item.defaultValue
            self._save()

    def get(self, item: ConfigItem):
        """ get config value """
        if item.group not in self._config:
            return item.defaultValue

        if item.name not in self._config[item.group]:
            return item.defaultValue

        value = self._config[item.group][item.name]

        # validate value
        if item.validator and not item.validator.validate(value):
            value = item.defaultValue
            self._config[item.group][item.name] = value
            self._save()

        return value

    def set(self, item: ConfigItem, value):
        """ set config value """
        if item.validator and not item.validator.validate(value):
            return False

        if item.group not in self._config:
            self._config[item.group] = {}

        self._config[item.group][item.name] = value
        self._save()
        return True

class Validator:
    """ Base validator """

    def validate(self, value):
        return True

class FolderValidator(Validator):
    """ Folder validator """

    def validate(self, value):
        return os.path.isdir(value) or not value

class IntValidator(Validator):
    """ Int validator """

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value):
        try:
            value = int(value)
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True
        except:
            return False

class EnumValidator(Validator):
    """ Enum validator """

    def __init__(self, enum):
        self.enum = enum

    def validate(self, value):
        return value in [e.value for e in self.enum]

# global config instance
cfg = Config()

# config items
cfg.dpiScale = ConfigItem("Appearance", "DpiScale", "Auto")
cfg.language = ConfigItem("General", "Language", "en_US")
cfg.downloadFolder = ConfigItem("Folders", "Download", "downloads", FolderValidator())
cfg.micaEnabled = ConfigItem("Appearance", "MicaEnabled", True)
cfg.theme = ConfigItem("Appearance", "Theme", "Auto")
cfg.maxConcurrentDownloads = ConfigItem("Download", "MaxConcurrentDownloads", 3, IntValidator(1, 10))
cfg.downloadFormat = ConfigItem("Download", "Format", "mp4")
cfg.downloadQuality = ConfigItem("Download", "Quality", "720p")
cfg.speedLimit = ConfigItem("Download", "SpeedLimit", 0, IntValidator(0, 100))  # 0 = unlimited, MB/s
cfg.concurrentPlaylistDownloads = ConfigItem("Download", "ConcurrentPlaylistDownloads", 2, IntValidator(1, 5))
cfg.retryAttempts = ConfigItem("Download", "RetryAttempts", 3, IntValidator(1, 10))
cfg.historyLimit = ConfigItem("History", "Limit", 100, IntValidator(10, 1000))
cfg.downloadHistory = ConfigItem("History", "DownloadHistory", [])

# add config items
cfg.addItem(cfg.dpiScale)
cfg.addItem(cfg.language)
cfg.addItem(cfg.downloadFolder)
cfg.addItem(cfg.micaEnabled)
cfg.addItem(cfg.theme)
cfg.maxConcurrentDownloads
cfg.addItem(cfg.downloadFormat)
cfg.addItem(cfg.downloadQuality)
cfg.addItem(cfg.speedLimit)
cfg.addItem(cfg.concurrentPlaylistDownloads)
cfg.addItem(cfg.retryAttempts)
cfg.addItem(cfg.historyLimit)
cfg.addItem(cfg.downloadHistory)