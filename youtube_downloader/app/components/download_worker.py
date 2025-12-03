# coding: utf-8
"""
Download worker thread for handling YouTube downloads
"""
from PySide6.QtCore import QThread, Signal
import yt_dlp
import os
import time

from app.common.utils import clean_unicode_text, format_speed, format_eta
from app.common.logger import get_logger

logger = get_logger('DownloadWorker')


class DownloadWorker(QThread):
    """
    Worker thread for downloading YouTube videos
    
    Signals:
        progressUpdated: Emitted during download (progress%, video_id, speed, eta)
        downloadCompleted: Emitted when download finishes (video_id, file_path, title)
        downloadFailed: Emitted on error (video_id, error_message)
        videoInfoFetched: Emitted when video info is retrieved (title, duration, thumbnail_url)
    """
    
    progressUpdated = Signal(int, str, str, str)  # progress, video_id, speed, eta
    downloadCompleted = Signal(str, str, str)  # video_id, file_path, title
    downloadFailed = Signal(str, str)  # video_id, error_message
    videoInfoFetched = Signal(str, str, str)  # title, duration, thumbnail_url

    def __init__(self, url, download_path, quality, format_type, is_audio_only):
        super().__init__()
        self.url: str = url
        self.download_path = download_path
        self.quality = quality
        self.format_type = format_type
        self.is_audio_only = is_audio_only
        self._is_cancelled = False
        self._ydl = None  # Store yt-dlp instance for cancellation
        self._start_time = None
        
        logger.info(f"DownloadWorker created: URL={url[:50]}..., Quality={quality}, Format={format_type}, AudioOnly={is_audio_only}")

    def run(self):
        """Main thread execution"""
        self._start_time = time.time()
        logger.info("Download worker started")
        
        try:
            if "playlist" in self.url.lower() or "list=" in self.url.lower():
                logger.info("Detected playlist URL")
                self.download_playlist()
            else:
                logger.info("Detected single video URL")
                self.download_video()
        except Exception as e:
            logger.error(f"Download failed with exception: {str(e)}", exc_info=True)
            self.downloadFailed.emit("unknown", str(e))
        finally:
            duration = time.time() - self._start_time
            logger.info(f"Download worker finished (took {duration:.2f}s)")

    def download_video(self):
        """Download a single video"""
        logger.info(f"Starting video download: {self.url}")
        try:
            # Set up yt-dlp options
            ydl_opts = {
                'format': self.get_format_string(),
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,  # Disable console progress output
                'restrictfilenames': False,
                'windowsfilenames': True,  # Use Windows-safe filenames
            }

            if self.is_audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format_type.lower(),
                    'preferredquality': '192',
                }]

            # Ensure download directory exists
            os.makedirs(self.download_path, exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First, fetch video info
                info_dict = ydl.extract_info(self.url, download=False)
                if info_dict:
                    title = info_dict.get('title', 'Unknown')
                    duration = str(info_dict.get('duration', 0))
                    thumbnail = info_dict.get('thumbnail', '')
                    self.videoInfoFetched.emit(title, duration, thumbnail)
                
                # Now download
                info_dict = ydl.extract_info(self.url, download=True)
                video_id = info_dict.get('id', 'unknown')
                title = info_dict.get('title', 'Unknown')
                file_path = ydl.prepare_filename(info_dict)

                if not self._is_cancelled:
                    logger.info(f"Video download completed: {title} -> {file_path}")
                    self.downloadCompleted.emit(video_id, file_path, title)
                else:
                    logger.warning("Download was cancelled")

        except Exception as e:
            logger.error(f"Video download failed: {str(e)}", exc_info=True)
            self.downloadFailed.emit("unknown", str(e))

    def download_playlist(self):
        """Download a playlist"""
        try:
            # Set up yt-dlp options for playlist
            ydl_opts = {
                'format': self.get_format_string(),
                'outtmpl': os.path.join(self.download_path, '%(playlist_title)s', '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'ignoreerrors': True,
                'restrictfilenames': False,
                'windowsfilenames': True,
            }

            if self.is_audio_only:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format_type.lower(),
                    'preferredquality': '192',
                }]

            # Ensure download directory exists
            os.makedirs(self.download_path, exist_ok=True)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url, download=True)

                # Get list of downloaded files
                if 'entries' in info_dict:
                    for entry in info_dict['entries']:
                        if entry and not self._is_cancelled:
                            video_id = entry.get('id', 'unknown')
                            title = entry.get('title', 'Unknown')
                            file_path = ydl.prepare_filename(entry)
                            self.downloadCompleted.emit(video_id, file_path, title)

        except Exception as e:
            self.downloadFailed.emit("unknown", f"Playlist download failed: {str(e)}")

    def get_format_string(self):
        """Get the appropriate format string for yt-dlp"""
        if self.is_audio_only:
            return 'bestaudio/best'

        # Map quality to yt-dlp format selectors
        quality_map = {
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "Best Available": "bestvideo+bestaudio/best"
        }

        format_str = quality_map.get(self.quality, "bestvideo+bestaudio/best")

        # Add format preference if specified
        if self.format_type.lower() != "best":
            format_str += f"/best[ext={self.format_type.lower()}]"

        return format_str

    def progress_hook(self, d):
        """
        Handle progress updates from yt-dlp
        
        Args:
            d: Dictionary with progress information
               - status: 'downloading', 'finished', 'error'
               - downloaded_bytes: bytes downloaded so far
               - total_bytes: total file size (if known)
               - total_bytes_estimate: estimated total (if exact unknown)
               - speed: download speed in bytes/sec
               - eta: estimated time remaining in seconds
               - _percent_str: formatted percentage string
               - _speed_str: formatted speed string
               - _eta_str: formatted ETA string
               - filename: output file path
               - info_dict: video metadata
        """
        if self._is_cancelled:
            return

        status = d.get('status')
        
        if status == 'downloading':
            # Get video info
            info_dict = d.get('info_dict', {})
            video_id = info_dict.get('id', 'unknown')
            
            # Calculate progress percentage (prefer raw bytes for accuracy)
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            
            if total > 0:
                progress_int = int((downloaded / total) * 100)
            else:
                # Fallback: parse formatted string
                percent_str = d.get('_percent_str', '0%')
                try:
                    progress_int = int(float(percent_str.replace('%', '').strip()))
                except (ValueError, AttributeError):
                    progress_int = 0
            
            # Get speed (prefer raw bytes/sec for accuracy)
            speed_bytes = d.get('speed')
            if speed_bytes and speed_bytes > 0:
                speed = format_speed(speed_bytes)
            else:
                # Fallback: use formatted string (clean Unicode)
                speed = clean_unicode_text(d.get('_speed_str', 'Calculating...'))
                if not speed or speed == 'N/A':
                    speed = 'Calculating...'
            
            # Get ETA (prefer raw seconds for accuracy)
            eta_seconds = d.get('eta')
            if eta_seconds and eta_seconds > 0:
                eta = format_eta(eta_seconds)
            else:
                # Fallback: use formatted string (clean Unicode)
                eta = clean_unicode_text(d.get('_eta_str', 'Calculating...'))
                if not eta or eta == 'N/A' or eta == 'Unknown':
                    eta = 'Calculating...'
            
            # Log progress periodically (every 10%)
            if progress_int % 10 == 0 and progress_int > 0:
                logger.debug(f"Download progress: {progress_int}% | Speed: {speed} | ETA: {eta}")
            
            self.progressUpdated.emit(progress_int, video_id, speed, eta)
            
        elif status == 'finished':
            # Download finished, post-processing may occur
            filename = d.get('filename', 'unknown')
            logger.info(f"Download finished: {filename}")
            
        elif status == 'error':
            # Error occurred
            logger.error(f"Download error in progress hook")

    def cancel(self):
        """Cancel the download"""
        logger.info("Cancel requested")
        self._is_cancelled = True
        # Force terminate the thread if it's stuck
        if self.isRunning():
            logger.warning("Terminating worker thread")
            self.terminate()
            self.wait(1000)  # Wait up to 1 second
            logger.info("Worker thread terminated")
