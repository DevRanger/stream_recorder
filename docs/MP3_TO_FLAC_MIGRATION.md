# MP3 to FLAC Migration - Reference Updates

## Summary

Updated all hardcoded MP3 references throughout the codebase to support both MP3 and FLAC files, ensuring full compatibility with the new FLAC-based recording system.

## Files Updated

### 1. **Cleanup Scripts**
- **`scripts/cleanup_old_recordings.sh`**
  - Updated file counting to include both `*.mp3` and `*.flac` files
  - Updated cleanup logic to remove both MP3 and FLAC files older than 7 days
  - Updated variable names from `REMOVED_MP3`/`MP3_COUNT` to `REMOVED_AUDIO`/`AUDIO_COUNT`
  - Updated log messages to reflect audio files instead of just MP3

- **`cleanup_old_recordings.sh`** (root directory)
  - Same updates as above for backward compatibility

### 2. **Backend API (`main.py`)**
- **`/api/temp-status` endpoint**
  - Updated temp file scanning to include both `temp_*.mp3` and `temp_*.flac` patterns
  - Uses glob patterns for both file types

### 3. **Audio Recorder (`audio_recorder.py`)**
- **`cleanup_related_temp_files()`**
  - Scans for both `temp_*.mp3` and `temp_*.flac` files in channel directories

- **`cleanup_temp_files()`**
  - Updated to find both MP3 and FLAC temp files across all channels

- **`cleanup_all_temp_files()`**
  - Updated to remove both MP3 and FLAC temp files immediately

- **`cleanup_temp_files_for_channel()`**
  - Updated to handle both file types for specific channel cleanup

- **`cleanup_orphaned_temp_files()`**
  - Updated to detect orphaned temp files in both formats

### 4. **Development Tools**
- **`dev/channel_health_monitor.py`**
  - Updated file filtering to include both `.mp3` and `.flac` files
  - Maintains exclusion of temp files

- **`dev/test_voice_detection.py`**
  - Updated to scan for both MP3 and FLAC files in recent recordings analysis
  - Uses separate glob patterns then combines results

### 5. **Documentation**
- **`scripts/README.md`**
  - Updated description to mention MP3, FLAC, and JSON file cleanup

## Technical Details

### Pattern Updates
**Before:**
```bash
find "$AUDIO_DIR" -type f -name "*.mp3" -mtime +$DAYS_OLD
```

**After:**
```bash
find "$AUDIO_DIR" -type f \( -name "*.mp3" -o -name "*.flac" \) -mtime +$DAYS_OLD
```

### Python Glob Patterns
**Before:**
```python
temp_pattern = os.path.join(self.output_dir, "*", "temp_*.mp3")
temp_files = glob.glob(temp_pattern)
```

**After:**
```python
temp_pattern_mp3 = os.path.join(self.output_dir, "*", "temp_*.mp3")
temp_pattern_flac = os.path.join(self.output_dir, "*", "temp_*.flac")
temp_files = glob.glob(temp_pattern_mp3) + glob.glob(temp_pattern_flac)
```

## Backward Compatibility

✅ **Maintained**: All existing MP3 files continue to work normally
✅ **Maintained**: Legacy temp file cleanup for MP3 files
✅ **Enhanced**: New FLAC files are properly handled by all cleanup routines

## Testing Verification

### Cleanup Scripts
```bash
# Test cleanup script
./scripts/cleanup_old_recordings.sh

# Should show:
# - Counts both MP3 and FLAC files
# - Removes both file types when older than 7 days
# - Logs "audio files" instead of "MP3 files"
```

### API Endpoints
```bash
# Test temp file status
curl http://127.0.0.1:8000/api/temp-status

# Should return counts for both MP3 and FLAC temp files
```

### Python Cleanup Functions
```python
# Test in Python console
from audio_recorder import AudioRecorder
ar = AudioRecorder({})

# Test cleanup functions
ar.cleanup_temp_files()           # Cleans both formats
ar.cleanup_all_temp_files()       # Removes both formats
ar.cleanup_orphaned_temp_files()  # Detects both formats
```

## Impact Summary

- **No Breaking Changes**: All existing functionality preserved
- **Enhanced Coverage**: Cleanup now handles FLAC files properly  
- **Future-Proof**: Scripts work with current FLAC recordings and legacy MP3 files
- **Consistent Logging**: All cleanup operations now report "audio files" terminology

## Files Not Changed (Intentionally)

1. **`audio_recorder.py` line 164**: `filename = f"{timestamp}_{channel_id}.mp3"`
   - This is legacy code for MP3 creation, kept for compatibility
   - New recordings use AudioProcessor which creates FLAC files

2. **Test files and documentation examples**: 
   - Maintain specific file extension examples for clarity
   - Show both MP3 and FLAC support in documentation

This update ensures that all cleanup and maintenance operations work seamlessly with the new FLAC recording format while maintaining full backward compatibility with existing MP3 files.
