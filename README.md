# YouTube Downloader Pro

A modern, feature-rich YouTube downloader application built with PySide6 and yt-dlp.

## Features

### Core Functionality
- **Single Video Download**: Download individual YouTube videos
- **Batch Download**: Download multiple videos at once
- **Playlist Support**: Download entire YouTube playlists
- **All Formats**: Support for MP4, WebM, MKV, MP3, M4A, WAV, FLAC
- **Quality Selection**: Choose from best quality down to 144p, plus audio-only
- **Playlist Management**: Add/remove URLs from batch download queue

### Advanced Features
- **Video Information**: Fetch and display video metadata before download
- **Subtitles**: Download automatic and manual subtitles
- **Thumbnails**: Download video thumbnails
- **Metadata**: Add metadata to downloaded files
- **Dark Theme**: Modern dark UI theme
- **Progress Tracking**: Real-time download progress with cancellation
- **Download History**: Track all downloads with status and timestamps
- **Resume Downloads**: Resume interrupted downloads
- **Skip Existing**: Option to skip already downloaded files

### User Interface
- **Tabbed Interface**: Organized tabs for different functions
- **Settings Panel**: Configurable download preferences
- **Modern GUI**: Clean, intuitive interface with dark theme
- **Real-time Feedback**: Status updates and progress indicators
- **Error Handling**: Comprehensive error messages and recovery

## Installation

### Prerequisites
- Python 3.7 or higher
- FFmpeg (for video processing and audio extraction)

### Quick Setup

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg**:
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

3. **Run the Application**:
   ```bash
   python launch.py
   ```

## Usage Guide

### Single Video Download

1. **Enter URL**: Paste a YouTube URL in the "Video URL" field
2. **Get Info**: Click "Get Video Info" to fetch metadata
3. **Choose Options**:
   - **Quality**: Select from Best, Worst, or specific resolutions (720p, 480p, etc.)
   - **Format**: Choose video format (MP4, WebM, MKV) or audio format (MP3, M4A, WAV, FLAC)
   - **Audio Only**: Select "Audio Only (MP3)" for music downloads
4. **Additional Options**:
   - Download subtitles
   - Download thumbnails
   - Add metadata to files
5. **Select Path**: Choose download directory or use default (Downloads folder)
6. **Download**: Click "Download" to start

### Batch Download

1. **Switch to Batch Tab**: Click the "Batch Download" tab
2. **Add URLs**: 
   - Enter URLs in the text field
   - Click "Add to List" to queue them
   - Use "Clear List" to remove all URLs
3. **Configure Options**: Set quality, format, and additional options (same as single download)
4. **Start Batch**: Click "Download All" to process the entire list
5. **Monitor Progress**: Track individual and overall progress

### Settings Configuration

1. **Switch to Settings Tab**: Click the "Settings" tab
2. **General Settings**:
   - **Max Concurrent Downloads**: Limit simultaneous downloads (1-10)
   - **Audio Quality**: Set audio bitrate for audio-only downloads (64-320 kbps)
3. **Advanced Settings**:
   - **Resume Downloads**: Continue interrupted downloads
   - **Skip Existing**: Don't re-download files that already exist
   - **Write Description**: Save video descriptions to separate files

### Download History

1. **View History**: Switch to the "History" tab
2. **Track Downloads**: See all previous downloads with status and timestamps
3. **Clear History**: Use "Clear History" to remove all entries

## Supported URL Formats

- **Standard Videos**: `https://www.youtube.com/watch?v=VIDEO_ID`
- **Shorts**: `https://www.youtube.com/shorts/VIDEO_ID`
- **Playlists**: `https://www.youtube.com/playlist?list=PLAYLIST_ID`
- **Channel Videos**: `https://www.youtube.com/@channelname/videos`
- **Live Streams**: Supported for VOD (Video on Demand) after completion

## Quality Options

| Quality | Resolution | Use Case |
|---------|------------|----------|
| Best | Highest available | General videos |
| Worst | Lowest available | Quick previews |
| 720p | 1280x720 | HD videos |
| 480p | 854x480 | Standard quality |
| 360p | 640x360 | Lower bandwidth |
| 240p | 426x240 | Very low bandwidth |
| 144p | 256x144 | Minimal bandwidth |
| Audio Only | No video | Music/podcasts |

## Format Options

### Video Formats
- **MP4**: Most compatible, good compression
- **WebM**: Modern format, better compression
- **MKV**: Container format, supports multiple audio/subtitle tracks

### Audio Formats
- **MP3**: Most compatible audio format
- **M4A**: High quality, smaller file size than MP3
- **WAV**: Uncompressed, highest quality
- **FLAC**: Lossless compression

## Troubleshooting

### Common Issues

1. **"FFmpeg not found"**:
   - Install FFmpeg and ensure it's in your system PATH
   - On Windows, you may need to restart your computer after installation

2. **"Unable to extract video data"**:
   - YouTube may have updated their anti-bot measures
   - Update yt-dlp: `pip install --upgrade yt-dlp`

3. **"Video is age-restricted or private"**:
   - Some videos require authentication or are geo-restricted
   - Try using cookies from a logged-in browser session

4. **Download speeds are slow**:
   - Check your internet connection
   - Reduce the number of concurrent downloads in settings
   - Try downloading during off-peak hours

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your internet connection
3. Ensure all dependencies are installed correctly
4. Try updating yt-dlp: `pip install --upgrade yt-dlp`

## File Structure

```
youtube_downloader/
├── youtube_downloader_gui.py  # Main application
├── launch.py                 # Launcher script
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── downloads/               # Default download directory
```

## Technical Details

### Dependencies
- **PySide6**: Modern Python Qt bindings for GUI
- **yt-dlp**: YouTube downloader library (fork of youtube-dl)
- **ffmpeg-python**: Python wrapper for FFmpeg

### Architecture
- **Multi-threading**: Downloads run in background threads to keep UI responsive
- **Progress tracking**: Real-time progress updates with detailed status
- **Error handling**: Comprehensive error recovery and user feedback
- **Memory efficient**: Streams processing to avoid memory issues with large files

## Legal Notice

This tool is for personal use only. Please respect:
- YouTube's Terms of Service
- Copyright laws in your jurisdiction
- Content creators' rights
- Local laws regarding content downloading

## License

This project is open source. Please see the license file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.