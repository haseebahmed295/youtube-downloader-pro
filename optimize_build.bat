@echo off
REM Build Size Optimization Script
REM This script removes unnecessary files before building

echo ========================================
echo Ytp Downloader Build Optimizer
echo ========================================
echo.

echo [1/4] Removing scipy from requirements...
pip uninstall -y scipy
echo.

echo [2/4] Cleaning PyQt-Fluent-Widgets examples (saves ~50MB)...
if exist "PyQt-Fluent-Widgets-PySide6\examples" (
    rmdir /s /q "PyQt-Fluent-Widgets-PySide6\examples"
    echo   - Removed examples folder
)
if exist "PyQt-Fluent-Widgets-PySide6\docs" (
    rmdir /s /q "PyQt-Fluent-Widgets-PySide6\docs"
    echo   - Removed docs folder
)
echo.

echo [3/4] Cleaning previous build artifacts...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo   - Cleaned build and dist folders
echo.

echo [4/4] Building optimized executable...
pyinstaller youtube_downloader.spec
echo.

if exist "dist\Ytp Downloader\Ytp Downloader.exe" (
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Output location: dist\Ytp Downloader\
    echo.
    echo Checking size...
    dir "dist\Ytp Downloader" /s
) else (
    echo ========================================
    echo Build failed! Check errors above.
    echo ========================================
)

pause
