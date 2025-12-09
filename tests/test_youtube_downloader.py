#!/usr/bin/env python3
# coding:utf-8

"""
Test script for Ytp Downloader functionality
"""

import os
import sys
import yt_dlp
from app.common.config import cfg

def test_youtube_downloader():
    """Test YouTube downloader functionality"""

    print("Testing Ytp Downloader...")

    # Test configuration
    print(f"Download folder: {cfg.get(cfg.downloadFolder)}")
    print(f"Default quality: {cfg.get(cfg.downloadQuality)}")
    print(f"Default format: {cfg.get(cfg.downloadFormat)}")

    # Test YouTube URL parsing (using a sample URL)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    try:
        # Set up yt-dlp options
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(test_url, download=False)
            print(f"Successfully parsed YouTube video: {info_dict.get('title', 'Unknown')}")
            print(f"Video ID: {info_dict.get('id', 'unknown')}")
            print(f"Author: {info_dict.get('uploader', 'Unknown')}")
            print(f"Duration: {info_dict.get('duration', 0)} seconds")

            # Test format selection
            formats = info_dict.get('formats', [])
            if formats:
                print(f"Available formats: {len(formats)}")
                # Find best video format
                best_format = None
                for fmt in formats:
                    if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                        if not best_format or fmt.get('height', 0) > best_format.get('height', 0):
                            best_format = fmt

                if best_format:
                    print(f"Selected format: {best_format.get('height', 'Unknown')}p {best_format.get('ext', 'Unknown')}")
                else:
                    print("No suitable format found")
            else:
                print("No formats available")

        print("✅ Ytp downloader functionality test passed!")

    except Exception as e:
        print(f"❌ Ytp downloader test failed: {e}")

    # Test configuration saving
    try:
        cfg.set(cfg.downloadQuality, "1080p")
        cfg.set(cfg.maxConcurrentDownloads, 5)
        print("✅ Configuration saving test passed!")
    except Exception as e:
        print(f"❌ Configuration saving test failed: {e}")

if __name__ == "__main__":
    test_youtube_downloader()