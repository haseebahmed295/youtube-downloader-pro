#!/bin/bash

echo "========================================"
echo "  YouTube Downloader Pro - Setup"
echo "========================================"
echo

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "Python found! Installing dependencies..."
echo

echo "Installing Python packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo
echo "You can now run the YouTube Downloader using:"
echo "  python3 launch.py"
echo
read -p "Press Enter to launch the application..."

python3 launch.py