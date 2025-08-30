# Development Directory

This directory contains development tools, test scripts, and debugging utilities for the Radio Stream Recorder with simplified RMS-based audio detection.

## Test Scripts

### Core System Tests
- **`test_channels.py`** - Test channel connectivity and configuration
- **`test_api.py`** - Test API endpoints and functionality  
- **`test_timestamp.py`** - Test timestamp generation and formatting
- **`test_volume_sensitivity.py`** - Test and tune volume sensitivity settings for RMS detection

### API Testing
- **`test_api.html`** - Web interface for testing API endpoints

## Debugging Tools

- **`debug_recording.py`** - Debug individual channel recording with RMS detection
- **`channel_health_monitor.py`** - Monitor channel health and stream connectivity

## Development Utilities

- **`cleanup_temp.py`** - Clean up temporary files during development
- **`quick_start.py`** - Quick startup script for testing multiple channels

## System Overview

The simplified system uses:
- **RMS-based audio detection** instead of complex voice analysis
- **Volume sensitivity thresholds** per channel (0.001-0.1 range)
- **FLAC output format** for final recordings
- **MP3 temp files** for streaming compatibility

## Volume Sensitivity Testing

Use `test_volume_sensitivity.py` to tune detection settings:

```bash
cd dev/
python test_volume_sensitivity.py
```

This will:
1. Record a test channel for 60 seconds
2. Analyze captured audio files
3. Provide tuning recommendations

## Quick Testing

Start recording on multiple channels:

```bash
cd dev/
python quick_start.py
```

Debug a single channel:

```bash
cd dev/
python debug_recording.py
```

## Legacy Files

Historical complex audio processing files have been moved to `../archive/dev_legacy/`:
- Legacy audio detection tests
- Noise gate tests  
- Complex transmission filtering tests
- Legacy HTML debugging interfaces

These are preserved for reference but are no longer relevant to the simplified system.
- **`test_api.html`** - API testing interface
- **`test_audio.html`** - Audio playback testing
- **`test_format.html`** - Audio format testing
- **`test_modal.html`** - Modal dialog testing
- **`test_modal_debug.html`** - Modal debugging
- **`test_page.html`** - General page testing

## Usage

Run test scripts from the project root:

```bash
# Audio processing tests
.venv/bin/python dev/test_noise_gate.py
.venv/bin/python dev/test_transmission_filter.py
.venv/bin/python dev/test_volume_sensitivity.py

# System tests
.venv/bin/python dev/test_channels.py
.venv/bin/python dev/test_api.py

# Debugging tools
.venv/bin/python dev/debug_recording.py
.venv/bin/python dev/channel_health_monitor.py
```

## Notes

- All test scripts are designed to be run independently
- Test scripts may create temporary files in the audio_files directory
- HTML files can be opened directly in a browser or served through the Flask application
- Development scripts may have additional dependencies beyond the main application requirements
