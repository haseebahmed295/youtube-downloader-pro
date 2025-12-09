@echo off
REM Build MSI only (skip PyInstaller build)
REM Use this when you already have the dist folder

echo ========================================
echo Build MSI Only (Skip PyInstaller)
echo ========================================
echo.

REM Check if dist exists
if not exist "..\dist\Ytp Downloader\Ytp Downloader.exe" (
    echo ERROR: dist folder not found!
    echo Run build.bat first to build the app
    pause
    exit /b 1
)

REM Check for WiX
where wix >nul 2>nul
if errorlevel 1 (
    echo ERROR: WiX not found
    echo Install: dotnet tool install --global wix
    pause
    exit /b 1
)

echo [1/4] Generating WiX installer file...
cd scripts
python generate_wix.py
cd ..
if errorlevel 1 (
    echo ERROR: WiX generation failed!
    pause
    exit /b 1
)
echo   Done
echo.

echo [2/4] Adding WiX extensions...
wix extension add WixToolset.UI.wixext 2>nul
wix extension add WixToolset.Util.wixext 2>nul
echo   Done
echo.

echo [3/4] Cleaning output folder...
if exist "output\*" del /q output\*
echo   Done
echo.

echo [4/4] Building MSI installer...
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
