# Scripts Directory

This directory contains all operational scripts for the Police Radio Stream Recorder.

## Operational Scripts

### Shell Scripts (.sh)

- **`start_recording.sh`** - Main recording control script with daemon support
  - Usage: `./start_recording.sh [--background|--daemon] [--stop] [--status] [--help]`
  - Features: Foreground/background modes, PID management, status monitoring
- **`start-web.sh`** - Web UI control script with Gunicorn support
  - Usage: `./start-web.sh [--background|--daemon] [--stop] [--status] [--help]`
  - Features: Production-ready Gunicorn server, daemon mode, status monitoring
- **`stop_recording.sh`** - Simple stop script (legacy, use start_recording.sh --stop instead)
  - Usage: `./stop_recording.sh`
- **`start-dev.sh`** - Development web server launcher
  - Usage: `./start-dev.sh`
  - Starts Flask development server on port 8000
- **`cleanup_old_recordings.sh`** - Automated cleanup of old recordings
  - Usage: `./cleanup_old_recordings.sh`
  - Removes MP3 and JSON files older than 7 days from project root audio_files directory
  - Suitable for cron jobs, logs to project root cleanup.log
- **`cleanup_temp_files.sh`** - Clean up temporary audio files
  - Usage: `./cleanup_temp_files.sh` (removes temp files older than 1 hour)
  - Usage: `./cleanup_temp_files.sh force` (removes ALL temp files)
  - Helpful for cleaning up orphaned temp files from interrupted recordings

- **`install-systemd-service.sh`** - Systemd service installer for web UI
  - Usage: `./install-systemd-service.sh`
  - Installs web UI as systemd service for production deployment

### Python Scripts (.py)

- **`start_recording.py`** - Main recording application entry point
- **`stop_recording.py`** - Recording stop functionality

## Master Control Script

From the project root, you can use `./recorder.sh` for unified access:

```bash
# Master control (recommended)
./recorder.sh start --background    # Start recording (daemon)
./recorder.sh status                # Check recording status
./recorder.sh stop                  # Stop recording
./recorder.sh web --background      # Start web UI (daemon)
./recorder.sh web-status            # Check web UI status
./recorder.sh web-stop              # Stop web UI
./recorder.sh dev                   # Start development server
./recorder.sh cleanup               # Clean old files
./recorder.sh help                  # Show help

# Direct access if needed
./scripts/start_recording.sh --background
./scripts/start-web.sh --background
./scripts/stop_recording.sh
```

## Directory Structure

```
scripts/
├── README.md                    # This file
├── start_recording.sh           # Main control script
├── stop_recording.sh            # Legacy stop script
├── start-dev.sh                 # Development server
├── cleanup_old_recordings.sh    # File cleanup
├── start_recording.py           # Recording application
└── stop_recording.py            # Stop functionality
```

## Notes

- All scripts are designed to work from any directory
- Shell scripts automatically locate the project root and virtual environment
- Python scripts should be run through the shell scripts for proper environment setup
- Log files and PID files are created in the project root directory
