# coding: utf-8
"""
Logging configuration for Ytp Downloader
"""
import logging
import os
import sys
from datetime import datetime
from PySide6.QtCore import QStandardPaths


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if sys.stdout.isatty():  # Only add colors if output is a terminal
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(name='YouTubeDownloader', level=logging.INFO):
    """
    Set up application logger with file and console handlers
    Each session creates a new log file with timestamp
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory
    log_dir = os.path.join(
        QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
        'YouTubeDownloader',
        'logs'
    )
    os.makedirs(log_dir, exist_ok=True)
    
    # Session-based log file with timestamp
    session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'session_{session_timestamp}.log')
    
    # File handler for session log (no rotation needed since each session has its own file)
    file_handler = logging.FileHandler(
        log_file,
        mode='w',  # Write mode - new file for each session
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)  # Use specified level for console
    
    # Formatters
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_format = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_handler.setFormatter(file_format)
    console_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup
    logger.info("=" * 80)
    logger.info(f"Ytp Downloader started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 80)
    
    return logger


def get_logger(name=None):
    """
    Get logger instance
    
    Args:
        name: Logger name (optional, uses module name if not provided)
        
    Returns:
        Logger instance
    """
    if name is None:
        # Get caller's module name
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'YouTubeDownloader')
    
    return logging.getLogger('YouTubeDownloader').getChild(name)


def log_exception(logger, exc_info=True):
    """
    Decorator to log exceptions in functions
    
    Args:
        logger: Logger instance
        exc_info: Include exception traceback
        
    Example:
        @log_exception(logger)
        def my_function():
            # code that might raise exception
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Exception in {func.__name__}: {str(e)}",
                    exc_info=exc_info
                )
                raise
        return wrapper
    return decorator


class LoggerMixin:
    """Mixin class to add logging to any class"""
    
    @property
    def logger(self):
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


# Example usage functions
def log_download_start(logger, url, quality, format_type):
    """Log download start"""
    logger.info(f"Starting download: URL={url}, Quality={quality}, Format={format_type}")


def log_download_progress(logger, progress, speed, eta):
    """Log download progress"""
    logger.debug(f"Download progress: {progress}% | Speed: {speed} | ETA: {eta}")


def log_download_complete(logger, file_path, duration):
    """Log download completion"""
    logger.info(f"Download completed: {file_path} (took {duration:.2f}s)")


def log_download_failed(logger, error):
    """Log download failure"""
    logger.error(f"Download failed: {error}")


def log_playlist_start(logger, url, count):
    """Log playlist download start"""
    logger.info(f"Starting playlist download: URL={url}, Videos={count}")


def log_playlist_complete(logger, success, failed):
    """Log playlist completion"""
    logger.info(f"Playlist download completed: {success} succeeded, {failed} failed")
