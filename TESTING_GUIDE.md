**For MS Store Reviewers and Testers**

## Application Overview

YouTube Downloader Pro is a desktop application for downloading YouTube videos and playlists with support for multiple formats and quality options.

## System Requirements

- **Operating System**: Windows 10/11
- **Internet Connection**: Required for downloading content from YouTube
- **Disk Space**: Minimum 500MB for application; additional space needed for downloads

## Installation Instructions

1. Run the installer executable
2. Follow the installation wizard
3. Launch from Start Menu or desktop shortcut

## Testing the Application

### First Launch
- Application will create configuration directories on first run
- Default download location: `[User]/Downloads/youtube_downloader`
- No account creation or login required

### Basic Functionality Tests

#### 1. Single Video Download
- Navigate to the "Download" tab
- Test URL: `https://www.youtube.com/watch?v=jNQXAC9IVRw` (Creative Commons video)
- Select quality: 720p
- Select format: MP4
- Click "Download" button
- Expected: Progress bar shows download status, file saves to download directory

#### 2. Playlist Download
- Navigate to the "Playlist" tab
- Test URL: `https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf` (Public playlist)
- Select concurrent downloads: 2
- Click "Download Playlist"
- Expected: Multiple videos download with progress tracking

#### 3. Audio-Only Download
- Use any video URL
- Check "Audio Only" option
- Select format: MP3
- Expected: Downloads audio file only, no video

#### 4. Download History
- Navigate to "History" tab
- Expected: Shows list of previously downloaded items with timestamps
- Test "Clear History" button
- Expected: History list clears

#### 5. Settings
- Navigate to "Settings" tab
- Change download directory
- Toggle theme (Light/Dark)
- Change default quality
- Expected: Settings persist after application restart

### Expected Behavior

#### Success Cases
- Valid YouTube URL → Download starts immediately
- Playlist URL → Shows video count and begins batch download
- Existing file → Option to skip or overwrite
- Network interruption → Error message displayed, can retry

#### Error Cases
- Invalid URL → Error message: "Invalid YouTube URL"
- No internet → Error message: "Network connection failed"
- Restricted video → Error message: "Video unavailable or restricted"
- Insufficient disk space → Error message: "Not enough disk space"

### Privacy and Data Testing

#### What to Verify
- No network requests to analytics services
- No user tracking or telemetry
- All data stored locally in application directory
- No cloud synchronization
- No account creation or authentication

### Performance Expectations

- Application launch: < 5 seconds
- Video info retrieval: 2-10 seconds (depends on network)
- Download speed: Limited by user's internet connection
- Memory usage: 100-300 MB during active downloads

### Known Limitations

1. **YouTube API Changes**: If YouTube changes their API, downloads may temporarily fail
2. **Format Availability**: Not all quality/format combinations available for every video
3. **Age-Restricted Content**: Cannot download age-restricted content
4. **Live Streams**: Cannot download ongoing live streams
5. **Premium Content**: Cannot download YouTube Premium exclusive content

### Troubleshooting Common Issues

#### "Video unavailable"
- Video may be private, deleted, or region-restricted
- Try a different test video

#### Downloads fail immediately
- Check internet connection
- Verify YouTube is accessible from test environment
- Check firewall/proxy settings

### Testing Checklist

- [ ] Application installs without errors
- [ ] Application launches successfully
- [ ] Single video download completes
- [ ] Playlist download works with multiple videos
- [ ] Audio-only extraction functions
- [ ] Quality selection works (144p to best available)
- [ ] Format selection works (MP4, WebM, MP3, etc.)
- [ ] Download history records and displays correctly
- [ ] Settings save and persist after restart
- [ ] Theme switching works (Light/Dark)
- [ ] Cancel download functionality works
- [ ] Error messages display appropriately
- [ ] Application uninstalls cleanly
- [ ] No personal data transmitted externally
- [ ] Local data can be deleted

### Security Considerations

- Application does not require administrator privileges
- Downloaded files are standard video/audio formats
- No automatic execution of downloaded files
- All network requests go to YouTube domains only

### Compliance Notes

- **Copyright**: Application is a tool; users responsible for legal use
- **YouTube ToS**: Users must comply with YouTube's Terms of Service
- **Privacy**: No personal data collected or transmitted

### Test Environment Recommendations

- Clean virtual machine or test system
- Stable internet connection (10+ Mbps recommended)
- At least 5GB free disk space
- Standard user account (not administrator)
- No VPN or proxy (for initial testing)

### Expected Test Duration

- Basic functionality: 30-45 minutes
- Comprehensive testing: 2-3 hours
- Stress testing (large playlists): Additional 1-2 hours

---

**Questions or Issues During Testing?**

If you encounter unexpected behavior:
1. Test with provided Creative Commons URLs
2. Ensure YouTube is accessible from your network
3. Try with a fresh installation

