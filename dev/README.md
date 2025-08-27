# Development Directory

This directory contains development tools, test scripts, and debugging utilities for the Police Radio Stream Recorder.

## Test Scripts

### Audio Processing Tests
- **`test_noise_gate.py`** - Test and tune noise gate parameters
- **`test_transmission_filter.py`** - Test transmission detection and filtering
- **`test_voice_detection.py`** - Test advanced voice detection algorithms

### System Tests
- **`test_channels.py`** - Test channel connectivity and configuration
- **`test_api.py`** - Test API endpoints and functionality
- **`test_timestamp.py`** - Test timestamp generation and formatting

## Debugging Tools

- **`debug_recording.py`** - Recording debugging utilities
- **`channel_health_monitor.py`** - Monitor channel health and activity

## Development Utilities

- **`cleanup_temp.py`** - Clean up temporary files during development
- **`quick_start.py`** - Quick development startup script

## Web Development Files

### HTML Test Pages
- **`debug_channels.html`** - Channel debugging interface
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
.venv/bin/python dev/test_voice_detection.py

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
