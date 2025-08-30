# Dev Directory Cleanup Summary

## Files Moved to Archive (dev_legacy/)

The following obsolete files have been moved to `archive/dev_legacy/` since they test features that were removed during the system simplification:

### Obsolete Test Scripts
- **`test_noise_gate.py`** - Tested noise gate features (removed)
- **`test_voice_detection.py`** - Tested advanced voice detection algorithms (simplified to RMS)
- **`test_transmission_filter.py`** - Tested complex transmission filtering (simplified)
- **`test_audio_processing.py`** - Tested complex audio processing (removed)

### Obsolete HTML Interfaces  
- **`debug_channels.html`** - Channel debugging web interface
- **`test_audio.html`** - Audio testing interface
- **`test_format.html`** - Format testing interface
- **`test_modal.html`** - Modal dialog testing
- **`test_modal_debug.html`** - Modal debugging interface
- **`test_page.html`** - General page testing

## Files Kept and Updated

### Updated for Simplified System
- **`debug_recording.py`** - Updated to show RMS detection info
- **`quick_start.py`** - Updated to show volume sensitivity settings
- **`README.md`** - Updated to reflect simplified system

### Still Relevant
- **`test_channels.py`** - Channel connectivity testing
- **`test_api.py`** - API endpoint testing
- **`test_api.html`** - API testing interface
- **`test_timestamp.py`** - Timestamp testing
- **`channel_health_monitor.py`** - Channel monitoring
- **`cleanup_temp.py`** - Development cleanup

### New Files Added
- **`test_volume_sensitivity.py`** - New tool for tuning RMS detection thresholds

## System Changes Reflected

The dev directory now reflects the simplified system:
- **RMS-based audio detection** instead of complex voice analysis
- **Volume sensitivity per channel** instead of noise gates
- **FLAC output format** instead of MP3
- **Simple threshold detection** instead of multi-factor analysis

## Usage

The remaining tools are focused on:
1. **Testing volume sensitivity settings** - The key tuning parameter
2. **Debugging connectivity issues** - Channel health and API testing  
3. **Quick development testing** - Fast startup and single-channel debugging

All obsolete complexity has been archived while preserving useful core functionality.

*Cleanup completed: August 29, 2025*
