# coding: utf-8
"""
Test URL extraction functionality
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'youtube_downloader'))

from app.common.utils import extract_video_id_from_url, is_playlist_only_url

# Test cases
test_urls = [
    # Video with playlist parameters (should extract clean video URL)
    "https://www.youtube.com/watch?v=nYuX1HoWPO0&list=RDm82P6WokM7I&index=13",
    
    # Short URL with playlist
    "https://youtu.be/nYuX1HoWPO0?list=PLxxx",
    
    # Standard video URL
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    
    # Pure playlist URL (should be rejected)
    "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
    
    # Embed URL
    "https://www.youtube.com/embed/nYuX1HoWPO0",
]

print("=" * 80)
print("URL EXTRACTION TEST")
print("=" * 80)

for url in test_urls:
    print(f"\nOriginal URL: {url}")
    
    # Check if playlist-only
    is_playlist = is_playlist_only_url(url)
    print(f"Is playlist-only: {is_playlist}")
    
    if is_playlist:
        print("❌ REJECTED - Use Playlist tab")
    else:
        # Extract clean URL
        clean_url, video_id = extract_video_id_from_url(url)
        if clean_url:
            print(f"✅ ACCEPTED")
            print(f"Clean URL: {clean_url}")
            print(f"Video ID: {video_id}")
        else:
            print("❌ INVALID - No video ID found")
    
    print("-" * 80)
