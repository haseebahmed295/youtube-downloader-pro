# coding: utf-8
"""
Concurrent playlist download worker - downloads multiple files simultaneously
"""
from PySide6.QtCore import QThread, Signal, QThreadPool, QRunnable, QObject
import yt_dlp
import os
import time
from queue import Queue
import threading

from app.common.utils import format_speed, format_eta, clean_unicode_text
from app.common.logger import get_logger
from app.common.config import cfg

logger = get_logger('ConcurrentPlaylistWorker')


class DownloadSignals(QObject):
    """Signals for download tasks"""
    started = Signal(int, int, str)  # index, total, title
    progress = Signal(int, int, str, str)  # index, progress%, speed, eta
    completed = Signal(int, str, str)  # index, file_path, title
    failed = Signal(int, str)  # index, error


class DownloadTask(QRunnable):
    """Individual download task for thread pool"""
    
    def __init__(self, index, total, video_url, title, download_opts, playlist_title, 
                 started_callback=None, progress_callback=None, completed_callback=None, failed_callback=None):
        super().__init__()
        self.index = index
        self.total = total
        self.video_url = video_url
        self.title = title
        self.download_opts = download_opts.copy()
        self.playlist_title = playlist_title
        self.signals = DownloadSignals()
        self._is_cancelled = False
        self.started_callback = started_callback
        self.progress_callback = progress_callback
        self.completed_callback = completed_callback
        self.failed_callback = failed_callback
        
        # Update output template for this specific file
        self.download_opts['outtmpl'] = os.path.join(
            self.download_opts['outtmpl_base'],
            self.playlist_title,
            f'{index} - %(title)s.%(ext)s'
        )
        
        # Set progress hook for this task
        self.download_opts['progress_hooks'] = [self.progress_hook]
        
    def progress_hook(self, d):
        """Handle progress for this specific download"""
        if self._is_cancelled or d.get('status') != 'downloading':
            return
            
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        
        progress = int((downloaded / total) * 100) if total > 0 else 0
        
        speed_bytes = d.get('speed')
        speed = format_speed(speed_bytes) if speed_bytes else 'Calculating...'
        
        eta_seconds = d.get('eta')
        eta = format_eta(eta_seconds) if eta_seconds else 'Calculating...'
        
        # Use callback instead of signal
        if self.progress_callback:
            self.progress_callback(self.index, progress, speed, eta)
        
    def run(self):
        """Execute download"""
        try:
            # Check if cancelled before starting
            if self._is_cancelled:
                logger.info(f"Task {self.index}/{self.total} cancelled before start: {self.title}")
                return
            
            # Log start and call callback
            logger.info(f"Task {self.index}/{self.total} started: {self.title}")
            
            # Call the callback directly instead of using signals (QRunnable signals don't work reliably)
            if self.started_callback:
                self.started_callback(self.index, self.total, self.title)
            
            # Check again before actual download
            if self._is_cancelled:
                logger.info(f"Task {self.index}/{self.total} cancelled during start: {self.title}")
                return
            
            with yt_dlp.YoutubeDL(self.download_opts) as ydl:
                video_info = ydl.extract_info(self.video_url, download=True)
                
                # Check if cancelled during download
                if self._is_cancelled:
                    logger.info(f"Task {self.index}/{self.total} cancelled during download: {self.title}")
                    return
                
                file_path = ydl.prepare_filename(video_info)
                
            logger.info(f"Task {self.index}/{self.total} completed: {self.title}")
            
            # Use callback for completion (only if not cancelled)
            if self.completed_callback and not self._is_cancelled:
                self.completed_callback(self.index, file_path, self.title)
            
        except Exception as e:
            logger.error(f"Task {self.index}/{self.total} failed: {str(e)}")
            
            # Use callback for failure
            if self.failed_callback:
                self.failed_callback(self.index, str(e))
            
    def cancel(self):
        """Cancel this download"""
        self._is_cancelled = True


class ConcurrentPlaylistWorker(QThread):
    """
    Worker for downloading playlists with concurrent downloads
    """
    
    playlistInfoFetched = Signal(str, int)
    fileStarted = Signal(int, int, str)
    fileProgress = Signal(int, int, str, str)
    fileCompleted = Signal(int, str, str)
    fileFailed = Signal(int, str)
    playlistCompleted = Signal(int, int)
    
    def __init__(self, url, download_path, quality, format_type, is_audio_only,
                 start_index=1, end_index=None, download_subtitles=False,
                 concurrent_downloads=2, speed_limit=0):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.quality = quality
        self.format_type = format_type
        self.is_audio_only = is_audio_only
        self.start_index = start_index
        self.end_index = end_index
        self.download_subtitles = download_subtitles
        self.concurrent_downloads = concurrent_downloads
        self.speed_limit = speed_limit  # MB/s, 0 = unlimited
        
        self._is_cancelled = False
        self._total_count = 0
        self._success_count = 0
        self._fail_count = 0
        self._active_tasks = {}
        self._thread_pool = QThreadPool()
        self._thread_pool.setMaxThreadCount(concurrent_downloads)
        
        logger.info(f"ConcurrentPlaylistWorker created: concurrent={concurrent_downloads}, speed_limit={speed_limit}MB/s")
        
    def run(self):
        """Main execution"""
        start_time = time.time()
        logger.info("Concurrent playlist worker started")
        
        try:
            self.download_playlist()
        except Exception as e:
            logger.error(f"Playlist download failed: {str(e)}", exc_info=True)
            self.fileFailed.emit(0, str(e))
        finally:
            duration = time.time() - start_time
            logger.info(f"Concurrent playlist worker finished: {self._success_count} succeeded, {self._fail_count} failed (took {duration:.2f}s)")
            self.playlistCompleted.emit(self._success_count, self._fail_count)
            
    def download_playlist(self):
        """Download playlist with concurrent downloads"""
        logger.info(f"Starting concurrent playlist download: {self.url}")
        
        # Step 1: Fast playlist info fetch
        info_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist',
        }
        
        if self.start_index > 1 or self.end_index:
            playlist_items = f"{self.start_index}:"
            if self.end_index:
                playlist_items = f"{self.start_index}:{self.end_index}"
            info_opts['playlist_items'] = playlist_items
            
        os.makedirs(self.download_path, exist_ok=True)
        
        # Get playlist info
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            logger.info("Fetching playlist info...")
            info_dict = ydl.extract_info(self.url, download=False)
            
            if not info_dict or 'entries' not in info_dict:
                raise Exception("Invalid playlist URL")
                
            playlist_title = info_dict.get('title', 'Playlist')
            entries = [e for e in info_dict['entries'] if e]
            self._total_count = len(entries)
            
            logger.info(f"Playlist: '{playlist_title}' with {self._total_count} videos")
            self.playlistInfoFetched.emit(playlist_title, self._total_count)
            
        # Step 2: Prepare download options
        download_opts = {
            'format': self.get_format_string(),
            'outtmpl_base': self.download_path,  # Base path
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
            'windowsfilenames': True,
        }
        
        # Add speed limit if specified
        if self.speed_limit > 0:
            download_opts['ratelimit'] = self.speed_limit * 1024 * 1024  # Convert MB/s to bytes/s
            logger.info(f"Speed limit set to {self.speed_limit} MB/s")
            
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
            
        # Step 3: Create and queue download tasks
        for index, entry in enumerate(entries, start=1):
            if self._is_cancelled:
                break
                
            video_url = entry.get('url') or entry.get('webpage_url') or entry.get('id')
            title = entry.get('title', f'Video {index}')
            
            if not video_url.startswith('http'):
                video_url = f"https://www.youtube.com/watch?v={video_url}"
                
            # Create download task with callbacks (QRunnable signals don't work reliably)
            task = DownloadTask(
                index, self._total_count, video_url, title, 
                download_opts, playlist_title,
                started_callback=self._on_task_started,
                progress_callback=self._on_task_progress,
                completed_callback=self._on_task_completed,
                failed_callback=self._on_task_failed
            )
            
            self._active_tasks[index] = task
            self._thread_pool.start(task)
            
        # Wait for all tasks to complete or timeout
        self._thread_pool.waitForDone(-1)  # Wait indefinitely
        
        # Log cancellation if it occurred
        if self._is_cancelled:
            logger.info("Playlist download was cancelled by user")
        
    def _on_task_started(self, index, total, title):
        """Handle task started"""
        # Don't emit if cancelled
        if self._is_cancelled:
            return
        logger.info(f"Worker received started callback for task {index}")
        self.fileStarted.emit(index, total, title)
    
    def _on_task_progress(self, index, progress, speed, eta):
        """Handle task progress"""
        # Don't emit if cancelled
        if self._is_cancelled:
            return
        self.fileProgress.emit(index, progress, speed, eta)
    
    def _on_task_completed(self, index, file_path, title):
        """Handle task completion"""
        # Don't emit if cancelled
        if self._is_cancelled:
            if index in self._active_tasks:
                del self._active_tasks[index]
            return
            
        self._success_count += 1
        self.fileCompleted.emit(index, file_path, title)
        if index in self._active_tasks:
            del self._active_tasks[index]
            
    def _on_task_failed(self, index, error):
        """Handle task failure"""
        # Don't emit if cancelled
        if self._is_cancelled:
            if index in self._active_tasks:
                del self._active_tasks[index]
            return
            
        self._fail_count += 1
        self.fileFailed.emit(index, error)
        if index in self._active_tasks:
            del self._active_tasks[index]
            
    def get_format_string(self):
        """Get format string for yt-dlp"""
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
        
    def cancel(self):
        """Cancel all downloads"""
        logger.info("Cancelling concurrent playlist downloads")
        self._is_cancelled = True
        
        # Cancel all active tasks
        for task in self._active_tasks.values():
            task.cancel()
        
        # Clear the thread pool to prevent new tasks from starting
        self._thread_pool.clear()
        
        # Give tasks a moment to check cancellation flag
        self._thread_pool.waitForDone(2000)
        
        # Force terminate the worker thread if still running
        if self.isRunning():
            logger.warning("Force terminating worker thread")
            self.terminate()
            self.wait(2000)
