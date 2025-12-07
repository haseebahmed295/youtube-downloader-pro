# Download Status Handling

## Overview

Comprehensive handling of all download states including interrupted downloads, playlist URL validation, and non-editable history items.

## Status Types

| Status | Badge | Color | Description |
|--------|-------|-------|-------------|
| Downloading | 🔵 Dot | Blue (#0078D4) | Download in progress |
| Success | ✅ Icon | Green (#10893E) | Download completed successfully |
| Failed | ❌ Icon | Red (#D13438) | Download failed with error |
| Cancelled | ⚠️ Icon | Orange (#F7630C) | User cancelled download |
| Interrupted | ⚠️ Icon | Dark Orange (#CA5010) | App closed during download |

## Features

### 1. Interrupted Download Detection

**Problem:** When the app closes during a download, the status remains "Downloading" forever.

**Solution:** On app startup, all "Downloading" entries are automatically changed to "Interrupted".

**Implementation:**
```python
# In MainWindow.__init__()
def cleanupIncompleteDownloads(self):
    """ Clean up downloads that were in progress when app closed """
    download_history = cfg.get(cfg.downloadHistory) or []
    modified = False
    
    for entry in download_history:
        if entry.get('status') == 'Downloading':
            entry['status'] = 'Interrupted'
            modified = True
    
    if modified:
        cfg.set(cfg.downloadHistory, download_history)
        self.historyInterface.refreshHistory()
```

**User Experience:**
- User starts download
- App crashes or is force-closed
- User reopens app
- History shows "Interrupted" status with dark orange badge
- Clear indication that download didn't complete

### 2. Playlist URL Validation in Single Download

**Problem:** Users might paste playlist URLs in the single download tab.

**Solution:** Detect and reject pure playlist URLs, but allow video URLs that happen to be in a playlist.

**URL Types:**

✅ **Allowed in Single Download:**
```
https://www.youtube.com/watch?v=LYOC_aAy1DQ
https://www.youtube.com/watch?v=LYOC_aAy1DQ&list=RDLYOC_aAy1DQ
https://youtu.be/LYOC_aAy1DQ
https://youtu.be/LYOC_aAy1DQ?list=PLxxx
```
These have a video ID (`v=` or `youtu.be/`) so they download just that single video.

❌ **Rejected in Single Download:**
```
https://www.youtube.com/playlist?list=PLdUpQq8gnItXY56ebTT0Kyy4JNiToYaqZ
https://www.youtube.com/playlist?list=PLxxx
```
These are pure playlist URLs with no video ID.

**Implementation:**
```python
def is_playlist_only_url(self, url):
    """ Check if URL is a pure playlist URL (no video ID) """
    if 'youtube.com' not in url and 'youtu.be' not in url:
        return False
    
    # Pure playlist URL pattern
    if '/playlist?' in url and 'list=' in url:
        return True
    
    # Has video ID - it's a single video
    if 'v=' in url or 'youtu.be/' in url:
        return False
    
    # Has list= but no video indicator
    if 'list=' in url and '/watch' not in url:
        return True
    
    return False
```

**Error Message:**
```
"This is a playlist URL. Please use the Playlist tab to download playlists."
```

### 3. Non-Editable History Items

**Problem:** Users could accidentally edit history table items by double-clicking.

**Solution:** All table items have the `ItemIsEditable` flag removed.

**Implementation:**

**Main History Table:**
```python
time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)
path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
```

**Playlist Details Dialog:**
```python
title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)
path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
```

**User Experience:**
- Double-click still works for opening files/viewing details
- But text cannot be edited
- Prevents accidental modifications

## Workflow Examples

### Example 1: App Closes During Download

1. User starts downloading "My Video"
2. History shows: 🔵 Downloading | My Video
3. App crashes or user force-closes
4. User reopens app
5. `cleanupIncompleteDownloads()` runs
6. History shows: ⚠️ Interrupted | My Video
7. User knows download didn't complete

### Example 2: Playlist URL in Single Download

1. User copies playlist URL: `https://www.youtube.com/playlist?list=PLxxx`
2. Pastes in Single Download tab
3. Clicks Download
4. Error message: "This is a playlist URL. Please use the Playlist tab..."
5. User switches to Playlist tab
6. Downloads successfully

### Example 3: Video from Playlist in Single Download

1. User copies video URL: `https://www.youtube.com/watch?v=abc&list=PLxxx`
2. Pastes in Single Download tab
3. Clicks Download
4. ✅ Downloads just that single video (not the whole playlist)
5. History shows: ✅ Success | Video Title

### Example 4: Trying to Edit History

1. User views history
2. Double-clicks on title column
3. Nothing happens (non-editable)
4. Double-clicks on path column
5. File opens (double-click action works)
6. History data remains protected

## Technical Details

### Startup Cleanup Timing

```
App Launch
    ↓
MainWindow.__init__()
    ↓
Create interfaces
    ↓
initNavigation()
    ↓
cleanupIncompleteDownloads() ← Runs here
    ↓
splashScreen.finish()
    ↓
App ready
```

### URL Validation Logic

```
URL Input
    ↓
Basic validation (http/https)
    ↓
is_playlist_only_url() check
    ↓
├─ True → Show error, stop
    ↓
└─ False → Continue with download
```

### Status Badge Colors

```css
Downloading:  #0078D4  (Blue - in progress)
Success:      #10893E  (Green - completed)
Failed:       #D13438  (Red - error)
Cancelled:    #F7630C  (Orange - user action)
Interrupted:  #CA5010  (Dark Orange - system issue)
```

## Configuration

No additional configuration needed. All features work automatically:
- Cleanup runs on every app start
- URL validation runs on every download attempt
- Non-editable flags set when creating table items

## Testing Checklist

- [x] App closes during single download → Shows "Interrupted" on restart
- [x] App closes during playlist download → Shows "Interrupted" on restart
- [x] Pure playlist URL in single download → Shows error message
- [x] Video URL with playlist parameter → Downloads single video
- [x] Cannot edit history table items
- [x] Cannot edit playlist details dialog items
- [x] Double-click still opens files/details
- [x] All status badges show correct colors
- [x] Cleanup runs automatically on startup
