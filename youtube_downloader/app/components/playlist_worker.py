# coding: utf-8
"""
Playlist download worker with individual file tracking
"""
from PySide6.QtCore import QThread, Signal
import yt_dlp
import os
import time

from app.common.utils import format_speed, format_eta
from app.common.logger import get_logger

logger = get_logger('PlaylistWorker')


class PlaylistDownloadWorker(QThread):
    """
    Worker thread for downloading YouTube playlists with individual file tracking
    
    Signals:
        playlistInfoFetched: Emitted when playlist info is retrieved (title, count)
        fileStarted: Emitted when a file starts downloading (index, total, title)
        fileProgress: Emitted during file download (index, progress%, speed, eta)
        fileCompleted: Emitted when a file finishes (index, file_path, title)
        fileFailed: Emitted when a file fails (index, error_message)
        playlistCompleted: Emitted when entire playlist finishes (success_count, fail_count)
    """
    
    playlistInfoFetched = Signal(str, int)  # playlist_title, video_count
    fileStarted = Signal(int, int, str)  # index, total, title
    fileProgress = Signal(int, int, str, str)  # index, progress%, speed, eta
    fileCompleted = Signal(int, str, str)  # index, file_path, title
    fileFailed = Signal(int, str)  # index, error_message
    playlistCompleted = Signal(int, int)  # success_count, fail_count

    def __init__(self, url, download_path, quality, format_type, is_audio_only, 
                 start_index=1, end_index=None, download_subtitles=False):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.quality = quality
        self.format_type = format_type
        self.is_audio_only = is_audio_only
        self.start_index = start_index
        self.end_index = end_index
        self.download_subtitles = download_subtitles
        self._is_cancelled = False
        self._current_index = 0
        self._total_count = 0
        self._success_count = 0
        self._fail_count = 0
        self._start_time = None
        
        logger.info(f"PlaylistWorker created: URL={url[:50]}..., Range={start_index}-{end_index or 'End'}, Subtitles={download_subtitles}")

    def run(self):
        """Main thread execution"""
        self._start_time = time.time()
        logger.info("Playlist worker started")
        
        try:
            self.download_playlist()
        except Exception as e:
            logger.error(f"Playlist download failed: {str(e)}", exc_info=True)
            self.fileFailed.emit(self._current_index, str(e))
        finally:
            duration = time.time() - self._start_time
            logger.info(f"Playlist worker finished: {self._success_count} succeeded, {self._fail_count} failed (took {duration:.2f}s)")
            self.playlistCompleted.emit(self._success_count, self._fail_count)

    def download_playlist(self):
        """Download playlist with individual file tracking"""
        logger.info(f"Starting playlist download: {self.url}")
        try:
            # First, get playlist info WITHOUT downloading
            info_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist',  # Fast playlist extraction
            }
            
            # Add playlist range if specified
            if self.start_index > 1 or self.end_index:
                playlist_items = f"{self.start_index}:"
                if self.end_index:
                    playlist_items = f"{self.start_index}:{self.end_index}"
                info_opts['playlist_items'] = playlist_items

            os.makedirs(self.download_path, exist_ok=True)

            # Get playlist info quickly
            with yt_dlp.YoutubeDL(info_opts) as ydl:
                logger.info("Fetching playlist info...")
                info_dict = ydl.extract_info(self.url, download=False)
                
                if not info_dict or 'entries' not in info_dict:
                    raise Exception("Invalid playlist URL or no videos found")
                
                playlist_title = info_dict.get('title', 'Playlist')
                entries = [e for e in info_dict['entries'] if e]
                self._total_count = len(entries)
                
                logger.info(f"Playlist info fetched: '{playlist_title}' with {self._total_count} videos")
                self.playlistInfoFetched.emit(playlist_title, self._total_count)
            
            # Now download each video individually
            download_opts = {
                'format': self.get_format_string(),
                'outtmpl': os.path.join(self.download_path, playlist_title, '%(playlist_index)s - %(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'windowsfilenames': True,
            }

            # Add subtitle download if enabled
            if self.download_subtitles:
                download_opts['writesubtitles'] = True
                download_opts['writeautomaticsub'] = True
                download_opts['subtitleslangs'] = ['en']

            if self.is_audio_only:
                download_opts['format'] = 'bestaudio/best'
                download_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.format_type.lower(),
                    'preferredquality': '192',
                }]

            # Download each video one by one
            with yt_dlp.YoutubeDL(download_opts) as ydl:
                for index, entry in enumerate(entries, start=1):
                    if self._is_cancelled:
                        break
                    
                    self._current_index = index
                    video_url = entry.get('url') or entry.get('webpage_url') or entry.get('id')
                    title = entry.get('title', f'Video {index}')
                    
                    # Emit file started
                    logger.info(f"Starting file {index}/{self._total_count}: {title}")
                    self.fileStarted.emit(index, self._total_count, title)
                    
                    try:
                        # Download this specific video
                        if video_url:
                            # If we have just an ID, construct the URL
                            if not video_url.startswith('http'):
                                video_url = f"https://www.youtube.com/watch?v={video_url}"
                            
                            video_info = ydl.extract_info(video_url, download=True)
                            file_path = ydl.prepare_filename(video_info)
                            
                            logger.info(f"File {index}/{self._total_count} completed: {title}")
                            self.fileCompleted.emit(index, file_path, title)
                            self._success_count += 1
                        else:
                            raise Exception("No video URL found")
                            
                    except Exception as e:
                        error_msg = str(e)
                        logger.warning(f"File {index}/{self._total_count} failed: {title} - {error_msg}")
                        self.fileFailed.emit(index, error_msg)
                        self._fail_count += 1

        except Exception as e:
            logger.error(f"Playlist download exception: {str(e)}", exc_info=True)
            self.fileFailed.emit(0, f"Playlist download failed: {str(e)}")

    def get_format_string(self):
        """Get the appropriate format string for yt-dlp"""
        if self.is_audio_only:
            return 'bestaudio/best'

        quality_map = {
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
            "Best Available": "bestvideo+bestaudio/best"
        }

        format_str = quality_map.get(self.quality, "bestvideo+bestaudio/best")

        if self.format_type.lower() != "best":
            format_str += f"/best[ext={self.format_type.lower()}]"

        return format_str

    def progress_hook(self, d):
        """
        Handle progress updates from yt-dlp for playlist downloads
        
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
               - info_dict: video metadata including playlist_index
        """
        if self._is_cancelled:
            return

        status = d.get('status')
        
        if status == 'downloading':
            # Get current file info from metadata
            info_dict = d.get('info_dict', {})
            playlist_index = info_dict.get('playlist_index', self._current_index)
            title = info_dict.get('title', f'Video {playlist_index}')
            filename = d.get('filename', '')
            
            # Note: We're downloading one file at a time now, so playlist_index
            # should match _current_index. If it doesn't, skip this update.
            if playlist_index and playlist_index != self._current_index:
                # This shouldn't happen with one-at-a-time downloads
                logger.warning(f"Playlist index mismatch: expected {self._current_index}, got {playlist_index}")
                return
            
            # Calculate progress percentage (prefer raw bytes)
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
            
            # Get speed (prefer raw bytes/sec)
            speed_bytes = d.get('speed')
            if speed_bytes and speed_bytes > 0:
                speed = format_speed(speed_bytes)
            else:
                # Fallback: use formatted string (MUST clean Unicode!)
                from app.common.utils import clean_unicode_text
                speed_str = d.get('_speed_str', 'Calculating...')
                speed = clean_unicode_text(speed_str) if speed_str else 'Calculating...'
                if not speed or speed == 'N/A':
                    speed = 'Calculating...'
            
            # Get ETA (prefer raw seconds)
            eta_seconds = d.get('eta')
            if eta_seconds and eta_seconds > 0:
                eta = format_eta(eta_seconds)
            else:
                # Fallback: use formatted string (MUST clean Unicode!)
                from app.common.utils import clean_unicode_text
                eta_str = d.get('_eta_str', 'Calculating...')
                eta = clean_unicode_text(eta_str) if eta_str else 'Calculating...'
                if not eta or eta in ('N/A', 'Unknown', ''):
                    eta = 'Calculating...'
            
            # Emit progress update
            self.fileProgress.emit(self._current_index, progress_int, speed, eta)
            
        elif status == 'finished':
            # File download finished
            filename = d.get('filename', 'unknown')
            logger.debug(f"File finished downloading: {filename}")
            
        elif status == 'error':
            # Error occurred
            logger.error(f"Download error in progress hook for file {self._current_index}")

    def cancel(self):
        """Cancel the download"""
        logger.info("Playlist cancel requested")
        self._is_cancelled = True
        if self.isRunning():
            logger.warning("Terminating playlist worker thread")
            self.terminate()
            self.wait(1000)
            logger.info("Playlist worker terminated")
