# Project Structure

## Directory Layout

```
youtube_downloader/           # Main application package
├── app/                      # Application modules
│   ├── common/              # Shared utilities and configuration
│   │   ├── config.py        # Application configuration management
│   │   ├── logger.py        # Logging setup and utilities
│   │   └── utils.py         # General utility functions
│   ├── components/          # Background workers and processing
│   │   ├── download_worker.py              # Single download worker
│   │   ├── playlist_worker.py              # Playlist processing
│   │   └── concurrent_playlist_worker.py   # Concurrent playlist downloads
│   ├── view/                # UI interfaces (Qt widgets)
│   │   ├── main_window.py                  # Main application window
│   │   ├── single_download_interface.py    # Single video download UI
│   │   ├── playlist_interface.py           # Playlist download UI
│   │   ├── history_interface.py            # Download history UI (separate tab)
│   │   ├── settings_interface.py           # Settings panel
│   │   └── about_interface.py              # About page
│   └── resource/            # Application resources
│       └── resource.py      # Resource management
├── main.py                  # Application entry point
└── run.py                   # Simple launcher script

PyQt-Fluent-Widgets-PySide6/  # Bundled UI library (submodule/vendored)
app/download/                 # Default download directory
```

## Architecture Patterns

- **MVC-style separation**: Views in `app/view/`, business logic in `app/components/`
- **Worker threads**: Background processing using Qt workers to keep UI responsive
- **Configuration management**: Centralized config in `app/common/config.py`
- **Logging**: Structured logging via `app/common/logger.py`
- **FluentWindow**: Main window extends `FluentWindow` from PyQt-Fluent-Widgets for modern UI
- **Separate interfaces**: Download, Playlist, and History are now separate tabs for better organization

## Code Organization Conventions

- **File naming**: Snake_case for Python files (e.g., `download_worker.py`)
- **Class naming**: PascalCase for classes (e.g., `MainWindow`, `DownloadWorker`)
- **Encoding declaration**: Files use `# coding: utf-8` or `# coding:utf-8` header
- **Interface suffix**: UI classes typically end with `Interface` (e.g., `SettingsInterface`)
- **Worker suffix**: Background processing classes end with `Worker`

## Import Conventions

- PySide6 imports grouped together (QtCore, QtGui, QtWidgets)
- qfluentwidgets imports on separate lines
- Local app imports use relative imports (`from app.common.config import cfg`)

## Key Files

- `requirements.txt`: Python dependencies
- `setup.bat` / `setup.sh`: Installation scripts
- `test.py`: UI component testing
- Root-level markdown files: Documentation for debugging and troubleshooting
