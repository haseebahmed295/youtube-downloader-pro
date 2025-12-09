# Ytp Downloader - Installer Build

This folder contains all the build scripts and assets needed to create the MSI installer.

## Folder Structure

```
installer_build/
├── assets/              # Installer assets (icons, images, license)
│   ├── app_icon.ico
│   ├── installer_banner.bmp
│   ├── installer_dialog.bmp
│   ├── license.rtf
│   └── LICENSE
├── scripts/             # Build scripts
│   └── generate_wix.py  # WiX XML generator
├── temp/                # Temporary build files (generated)
│   └── installer_generated.wxs
├── output/              # Final MSI output
│   └── YouTubeDownloaderPro-Setup-v1.0.0.msi
├── build.bat            # Full build (PyInstaller + MSI)
├── build_msi_only.bat   # MSI only (skip PyInstaller)
└── README.md            # This file
```

## Prerequisites

1. **Python 3.7+** with dependencies installed
2. **PyInstaller**: `pip install pyinstaller`
3. **WiX Toolset v4**: `dotnet tool install --global wix`

## Build Instructions

### Full Build (Recommended)

Builds the application with PyInstaller and creates the MSI installer:

```cmd
cd installer_build
build.bat
```

### MSI Only Build

If you already have the `dist` folder from a previous PyInstaller build:

```cmd
cd installer_build
build_msi_only.bat
```

## Build Process

1. **Clean**: Removes previous build artifacts
2. **PyInstaller**: Builds the executable to `dist/Ytp Downloader/`
3. **Generate WiX**: Creates `temp/installer_generated.wxs` with all files
4. **Add Extensions**: Ensures WiX UI extensions are available
5. **Build MSI**: Compiles the final installer to `output/`

## Output

The final installer will be created at:
```
installer_build/output/YouTubeDownloaderPro-Setup-v1.0.0.msi
```

## Troubleshooting

### WiX not found
```cmd
dotnet tool install --global wix
```

### PyInstaller not found
```cmd
pip install pyinstaller
```

### Missing dist folder
Run the full build with `build.bat` instead of `build_msi_only.bat`

### Build errors
Check the console output for specific error messages. Common issues:
- Missing dependencies in requirements.txt
- Incorrect file paths in generate_wix.py
- WiX XML syntax errors in generated file

## Customization

### Change Version
Edit the version in:
- `scripts/generate_wix.py` (line with `Version="1.0.0.0"`)
- `build.bat` and `build_msi_only.bat` (output filename)

### Update Assets
Replace files in the `assets/` folder:
- `app_icon.ico` - Application icon
- `installer_banner.bmp` - Top banner (493×58 pixels)
- `installer_dialog.bmp` - Welcome dialog (493×312 pixels)
- `license.rtf` - License agreement text

### Modify Installer Behavior
Edit `scripts/generate_wix.py` to customize:
- Installation directory
- Shortcuts (Start Menu, Desktop)
- Registry keys
- File associations
