# Application Tab Structure

## Navigation Tabs

```
┌─────────────────────────────────────────────────────────────┐
│  YouTube Downloader                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📥 Download      Single video downloads                   │
│  📚 Playlist      Playlist downloads with concurrent        │
│  📜 History       View all download history                 │
│  ⚙️  Settings      Application settings                      │
│  ℹ️  About         About information                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Tab Details

### 📥 Download Tab (FIF.DOWNLOAD)
**Purpose:** Download single YouTube videos

**Features:**
- URL input with validation
- Quality selection (Best, 1080p, 720p, 480p, 360p)
- Format selection (MP4, WEBM, 3GP)
- Audio-only mode with format options (MP3, AAC, OGG, WAV)
- Video info preview (title, duration)
- Progress bar with speed and ETA
- Cancel functionality
- Keyboard shortcut: Ctrl+Enter to download

**Saves to history:** Yes, with `type: 'single'`

---

### 📚 Playlist Tab (FIF.LIBRARY)
**Purpose:** Download entire YouTube playlists

**Features:**
- Playlist URL input
- Quality and format selection
- Audio-only mode
- Playlist range selection (start/end index)
- Subtitle download option
- Concurrent downloads (1-5 simultaneous)
- Speed limit control
- Individual file progress cards
- Success/fail statistics with badges
- Real-time progress tracking

**Saves to history:** Yes, with `type: 'playlist'` and all items

---

### 📜 History Tab (FIF.HISTORY)
**Purpose:** View and manage download history

**Features:**
- Table view with columns:
  - Type (Single 🎬 / Playlist 📚)
  - Status (Success ✅ / Failed ❌)
  - Date & Time (with "Today"/"Yesterday" formatting)
  - Title (with item count for playlists)
  - File Location (clickable)
- Search/filter functionality
- Export to CSV or TXT
- Context menu:
  - Open File
  - Open Folder
  - Copy Path
  - View Playlist Details (for playlists)
- **Double-click behavior:**
  - Single downloads: Opens the file
  - Playlist downloads: Opens details dialog showing all items
- Clear history option

---

### ⚙️ Settings Tab (FIF.SETTING)
**Purpose:** Configure application settings

**Features:**
- Download folder selection
- Theme selection (Auto/Light/Dark)
- Quality and format defaults
- History limit
- Concurrent download settings
- Speed limit settings
- Mica effect toggle

---

### ℹ️ About Tab (FIF.INFO)
**Purpose:** Application information

**Features:**
- Version information
- Credits
- License information
- Links to documentation

---

## History Entry Types

### Single Video Entry
```
Type: 🎬 Single
Status: ✅ Success
Time: Today 10:30:00
Title: Amazing Video Title
Location: amazing_video.mp4
```

### Playlist Entry
```
Type: 📚 Playlist
Status: ✅ Success (18/20)
Time: Today 10:30:00
Title: My Awesome Playlist (20 items)
Location: /downloads/My Awesome Playlist/
```

**Double-click opens dialog with:**
- Table of all 20 videos
- Individual status for each
- File locations
- Success/fail indicators

---

## Icon Reference

| Icon | Constant | Usage |
|------|----------|-------|
| 📥 | FIF.DOWNLOAD | Download tab |
| 📚 | FIF.LIBRARY | Playlist tab |
| 📜 | FIF.HISTORY | History tab |
| ⚙️ | FIF.SETTING | Settings tab |
| ℹ️ | FIF.INFO | About tab |
| 🎬 | FIF.VIDEO | Single video indicator |
| 📁 | FIF.FOLDER | Folder operations |
| ✅ | FIF.ACCEPT_MEDIUM | Success badge |
| ❌ | FIF.CANCEL_MEDIUM | Error badge |
| 🔍 | FIF.SEARCH | Search functionality |
| 💾 | FIF.SAVE | Export operations |
| 🗑️ | FIF.DELETE | Clear/delete operations |
| 📋 | FIF.COPY | Copy operations |

---

## Workflow Examples

### Download Single Video
1. Go to **Download** tab
2. Paste YouTube URL
3. Select quality and format
4. Click Download (or Ctrl+Enter)
5. View progress
6. Check **History** tab to see completed download

### Download Playlist
1. Go to **Playlist** tab
2. Paste playlist URL
3. Configure options (quality, concurrent downloads, etc.)
4. Click Download Playlist
5. Watch individual file progress cards
6. Check **History** tab to see playlist entry
7. Double-click playlist entry to see all items

### Review History
1. Go to **History** tab
2. Use search to filter entries
3. Double-click single videos to open them
4. Double-click playlists to see detailed breakdown
5. Right-click for context menu options
6. Export history if needed
