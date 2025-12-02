#!/usr/bin/env python3
# coding:utf-8

"""
Simple run script for YouTube Downloader
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()