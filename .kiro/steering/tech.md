# Technology Stack

## Core Technologies

- **Python**: 3.7+ required
- **PySide6**: Qt6 bindings for Python (GUI framework)
- **PyQt-Fluent-Widgets**: Modern Fluent Design UI components
- **yt-dlp**: YouTube download engine (youtube-dl fork)
- **FFmpeg**: Video/audio processing and format conversion

## Key Dependencies

```
PyQt-Fluent-Widgets[full]>=6.0.0
yt-dlp>=2023.7.6
ffmpeg-python>=0.2.0
PySide6>=6.4.2
PySideSix-Frameless-Window>=0.4.0
darkdetect
colorthief
scipy
pillow
```

## Common Commands

### Setup & Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Windows setup (automated)
setup.bat

# Linux/macOS setup (automated)
./setup.sh
```

### Running the Application
```bash
# Main entry point
python youtube_downloader/main.py

# Alternative launcher
python youtube_downloader/run.py
```

### Testing
```bash
# Run test file
python test.py

# Run badge tests
python test_badges.py
```

## External Requirements

- **FFmpeg**: Must be installed separately and available in system PATH
  - Windows: Download from ffmpeg.org
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

## Build System

No formal build system (setuptools/poetry) is currently configured. The application runs directly from Python source files.
