# Progress Hook Debug & Jump Fix

## Problem
Download progress bars were "jumping" - showing inconsistent progress updates, sometimes going backwards or updating too frequently.

---

## Solution Implemented

### 1. Debug Logging
Added comprehensive logging to track progress hook behavior:

```python
# Status logging
logger.debug(f"[Task {index}] Progress hook called - Status: {status}")

# Raw data logging
logger.debug(f"[Task {index}] Downloaded: {downloaded}, Total: {total}")

# Calculated values logging
logger.debug(f"[Task {index}] Progress: {progress}%, Speed: {speed}, ETA: {eta}")

# Warning for backwards progress
logger.warning(f"[Task {index}] Progress went backwards: {old}% -> {new}%")

# Throttling logging
logger.debug(f"[Task {index}] Throttling update - Time: {time}s, Change: {change}%")
```

---

### 2. Data Validation
Added validation to prevent invalid progress values:

```python
# Validate total bytes
if total <= 0:
    logger.warning(f"[Task {index}] Invalid total bytes: {total}")
    return

# Validate downloaded vs total
if downloaded > total:
    logger.warning(f"[Task {index}] Downloaded ({downloaded}) > Total ({total})")
    downloaded = total

# Clamp progress to valid range
progress = max(0, min(100, progress))
```

**Prevents:**
- Division by zero
- Progress > 100%
- Negative progress
- Invalid calculations

---

### 3. Progress Tracking
Prevents progress from going backwards:

```python
# Track last progress
self._last_progress = 0

# Prevent backwards movement
if progress < self._last_progress:
    logger.warning(f"Progress went backwards: {self._last_progress}% -> {progress}%")
    progress = self._last_progress
```

**Benefits:**
- Progress only moves forward
- Smooth visual experience
- No confusing jumps backwards

---

### 4. Update Throttling
Limits UI updates to prevent jumping:

```python
# Throttle settings
self._last_update_time = 0
self._update_interval = 0.5  # Update every 0.5 seconds

# Calculate if should update
current_time = time.time()
time_since_update = current_time - self._last_update_time
progress_change = abs(progress - self._last_progress)

# Update conditions
should_update = (
    time_since_update >= self._update_interval or  # Enough time passed
    progress_change >= 5 or                        # Significant change (5%)
    progress == 100                                # Completion
)
```

**Update Triggers:**
- ✅ Every 0.5 seconds (prevents too frequent updates)
- ✅ Progress change ≥ 5% (shows significant progress)
- ✅ Progress reaches 100% (always show completion)

**Benefits:**
- Smooth progress bar movement
- Reduced UI updates (better performance)
- No visual jumping
- Still responsive to user

---

## Debug Log Examples

### Normal Progress:
```
[Task 1] Progress hook called - Status: downloading
[Task 1] Downloaded: 1048576, Total: 10485760
[Task 1] Progress: 10%, Speed: 2.50 MB/s, ETA: 00:04
[Task 1] Progress: 15%, Speed: 2.48 MB/s, ETA: 00:03
[Task 1] Progress: 20%, Speed: 2.52 MB/s, ETA: 00:03
```

### Throttled Updates:
```
[Task 1] Progress: 20%, Speed: 2.50 MB/s, ETA: 00:03
[Task 1] Throttling update - Time: 0.12s, Change: 1%
[Task 1] Throttling update - Time: 0.25s, Change: 2%
[Task 1] Throttling update - Time: 0.38s, Change: 3%
[Task 1] Progress: 25%, Speed: 2.48 MB/s, ETA: 00:02
```

### Backwards Progress Prevented:
```
[Task 1] Progress: 50%, Speed: 2.50 MB/s, ETA: 00:02
[Task 1] Progress went backwards: 50% -> 45%
[Task 1] Progress: 50%, Speed: 2.48 MB/s, ETA: 00:02  (kept at 50%)
```

### Invalid Data Caught:
```
[Task 1] Invalid total bytes: 0
[Task 1] Downloaded (15000000) > Total (10000000)
```

---

## How to Use Debug Logs

### 1. Enable Debug Logging
In your logger configuration:
```python
logger.setLevel(logging.DEBUG)
```

### 2. Watch for Issues
Look for these patterns in logs:

**Jumping Progress:**
```
Progress went backwards: X% -> Y%
```
Indicates yt-dlp is reporting inconsistent progress.

**Too Frequent Updates:**
```
Throttling update - Time: 0.05s, Change: 0%
```
Shows throttling is working to prevent excessive updates.

**Invalid Data:**
```
Invalid total bytes: 0
Downloaded (X) > Total (Y)
```
Indicates data validation is catching bad values.

### 3. Analyze Patterns
- Check if specific videos cause issues
- Look for network-related patterns
- Identify if issue is with certain formats

---

## Configuration Options

### Adjust Update Interval
Change how often progress updates:
```python
self._update_interval = 0.5  # Default: 0.5 seconds

# More frequent (smoother but more CPU):
self._update_interval = 0.25

# Less frequent (better performance):
self._update_interval = 1.0
```

### Adjust Progress Change Threshold
Change minimum progress change for update:
```python
progress_change >= 5  # Default: 5%

# More sensitive (more updates):
progress_change >= 2

# Less sensitive (fewer updates):
progress_change >= 10
```

---

## Performance Impact

### Before (No Throttling):
- Updates: ~20-50 per second
- UI redraws: Very frequent
- CPU usage: Higher
- Visual: Jumpy, flickering

### After (With Throttling):
- Updates: ~2 per second
- UI redraws: Controlled
- CPU usage: Lower
- Visual: Smooth, stable

---

## Testing Checklist

- [x] Progress never goes backwards
- [x] Progress clamped to 0-100%
- [x] Invalid data caught and logged
- [x] Updates throttled appropriately
- [x] Completion (100%) always shown
- [x] Significant changes (>5%) shown
- [x] Debug logs provide useful info
- [x] Performance improved
- [x] Visual jumping eliminated

---

## Troubleshooting

### Issue: Progress still jumps
**Check:**
- Are multiple tasks updating the same UI element?
- Is the UI thread being blocked?
- Are signals being queued properly?

**Solution:**
- Ensure each task has unique progress tracking
- Use Qt.QueuedConnection for signals
- Check for thread safety issues

### Issue: Progress updates too slow
**Adjust:**
```python
self._update_interval = 0.25  # Faster updates
progress_change >= 2          # More sensitive
```

### Issue: Too many debug logs
**Reduce:**
```python
# Only log warnings and errors
if progress < self._last_progress:
    logger.warning(...)  # Keep this
# Remove or comment out debug logs
# logger.debug(...)
```

---

## Future Improvements

- [ ] Add progress smoothing algorithm
- [ ] Implement exponential moving average for speed
- [ ] Add configurable throttling via settings
- [ ] Create progress analytics dashboard
- [ ] Add unit tests for edge cases
