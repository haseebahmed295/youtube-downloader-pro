@echo off
REM Ytp Downloader - Complete Build Script
REM Organized build structure

echo ========================================
echo Ytp Downloader - Build Installer
echo ========================================
echo.

REM Check for WiX
where wix >nul 2>nul
if errorlevel 1 (
    echo ERROR: WiX not found
    echo Install: dotnet tool install --global wix
    pause
    exit /b 1
)

echo [1/5] Cleaning previous builds...
if exist "..\build" rmdir /s /q ..\build
if exist "..\dist" rmdir /s /q ..\dist
if exist "output\*" del /q output\*
if exist "temp\*" del /q temp\*
echo   Done
echo.

echo [2/5] Building executable with PyInstaller...
pyinstaller youtube_downloader.spec
if errorlevel 1 (
    echo ERROR: PyInstaller failed!
    pause
    exit /b 1
)
echo   Done
echo.

echo [3/5] Generating WiX installer file...
cd .\installer_build\scripts
python generate_wix.py
cd ..
if errorlevel 1 (
    echo ERROR: WiX generation failed!
    pause
    exit /b 1
)
echo   Done
echo.

echo [4/5] Adding WiX extensions...
wix extension add WixToolset.UI.wixext 2>nul
wix extension add WixToolset.Util.wixext 2>nul
echo   Done
echo.

echo [5/5] Building MSI installer...
wix build temp\installer_generated.wxs ^
    -arch x64 ^
    -ext WixToolset.UI.wixext ^
    -out output\YouTubeDownloaderPro-Setup-v1.0.0.msi

if errorlevel 1 (
    echo.
    echo ERROR: WiX build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.

if exist "output\YouTubeDownloaderPro-Setup-v1.0.0.msi" (
    for %%F in (output\*.msi) do (
        echo Installer: %%~nxF
        set /a size_mb=%%~zF/1024/1024
        echo Size: ~!size_mb! MB (%%~zF bytes)
        echo Location: %%~fF
    )
    echo.
    echo Ready to distribute!
)

echo.
pause
