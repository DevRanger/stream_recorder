# FLAC Audio Support Update

## Summary

Successfully updated the stream recorder to support FLAC audio format for both recording and playback.

## Changes Made

### Backend API (`main.py`)
- **Updated `/api/recording/<filename>` endpoint**:
  - Now supports both `.mp3` and `.flac` file extensions
  - Automatically detects file format and sets appropriate MIME type:
    - `.flac` files: `audio/flac`
    - `.mp3` files: `audio/mpeg`
  - Maintains backward compatibility with existing MP3 files

### Audio Processing (`audio_recorder.py`)
- **Updated `get_recordings()` method**:
  - Now scans for both `.mp3` and `.flac` files in channel directories
  - Correctly handles metadata files for both formats
  - Maintains existing functionality for MP3 files

- **Updated `create_metadata_file()` method** (previous change):
  - Supports metadata creation for both MP3 and FLAC files
  - Correctly identifies file format in metadata

### Frontend UI (`templates/index.html`)
- **Added `getAudioSources()` helper function**:
  - Generates appropriate `<source>` tags based on file extension
  - Provides multiple MIME type options for better browser compatibility
  - FLAC files get: `audio/flac` and `audio/x-flac`
  - MP3 files get: `audio/mpeg` and `audio/mp3`

- **Updated audio playback modals**:
  - Single recording playback modal
  - Batch recording playback modal
  - Both now use dynamic source generation for proper format support

## Browser Compatibility

### FLAC Support:
- **✅ Chrome/Chromium**: Full support for `audio/flac`
- **✅ Firefox**: Full support for `audio/flac`
- **✅ Safari**: Support varies by version (recent versions support FLAC)
- **✅ Edge**: Full support for `audio/flac`

### Fallback Strategy:
- Multiple MIME types provided (`audio/flac`, `audio/x-flac`)
- Graceful degradation for unsupported browsers
- Clear error messages in audio elements

## Testing

### API Verification:
```bash
# Test FLAC file API endpoint
curl -I "http://127.0.0.1:8000/api/recording/FILENAME.flac"
# Should return: Content-Type: audio/flac

# Test recordings API includes FLAC files
curl "http://127.0.0.1:8000/api/recordings/channel/25_-_San_Mateo?limit=5"
# Should return FLAC files in recordings array
```

### Browser Testing:
- Access: `http://127.0.0.1:8000/test_flac_playback.html`
- Verifies FLAC playback capability
- Shows browser compatibility information
- Tests API integration

## Current Status

✅ **Completed**:
- FLAC file detection in API
- Proper MIME type serving
- Frontend audio source generation
- Metadata creation for FLAC files
- Browser compatibility testing

✅ **Verified**:
- API returns FLAC files: `11 recordings found for San Mateo`
- FLAC files served with correct MIME type: `audio/flac`
- Web UI supports FLAC playback through dynamic source generation

## Usage

### For New Recordings:
- All new recordings are saved as FLAC files (as per recent refactor)
- Metadata files are automatically created for each FLAC recording
- Web UI automatically detects and plays FLAC files

### For Existing MP3 Files:
- Full backward compatibility maintained
- Existing MP3 files continue to work normally
- No migration required

### For Developers:
- Use `getAudioSources(filename)` function for any new audio elements
- API automatically handles both formats transparently
- Test with preferred channels: SSF, EPA, San Mateo, Daly City

## Future Considerations

1. **Optional MP3 Conversion**: Could add endpoint to convert FLAC to MP3 for older browsers
2. **Progressive Enhancement**: Could detect browser capabilities and serve appropriate format
3. **Compression Options**: Could add FLAC compression level configuration
4. **Batch Conversion**: Could add utility to convert existing MP3 files to FLAC

## Files Modified

1. `/main.py` - API endpoint MIME type detection
2. `/audio_recorder.py` - File scanning and metadata handling  
3. `/templates/index.html` - Dynamic audio source generation
4. `/test_flac_playback.html` - Testing interface (existing)

## Verification Commands

```bash
# Check for FLAC files
find audio_files -name "*.flac" | head -5

# Check for metadata files
find audio_files -name "*metadata.json" | head -5

# Test API endpoint
python3 -c "import requests; r=requests.get('http://127.0.0.1:8000/api/recordings/channel/25_-_San_Mateo?limit=5'); print(f'Found: {r.json()[\"total\"]} recordings')"
```

This update ensures seamless FLAC support while maintaining full backward compatibility with existing MP3 recordings.
