# Project Structure

## Overview

The Radio Stream Recorder project is now organized into a clean, modular structure that separates core functionality, utilities, documentation, and development tools.

## Directory Structure

```
stream_recorder/
├── README.md                   # Main project documentation
├── pyproject.toml             # Python project configuration
├── radio_channels.json        # Channel configuration
├── .gitignore                 # Git ignore patterns
├── .python-version            # Python version specification
├── uv.lock                    # Dependency lock file
│
├── main.py                    # Main Flask application
├── audio_recorder.py          # Core recording engine
├── config.py                  # Configuration management
├── start_recording.py         # Standalone recording script
├── stop_recording.py          # Standalone stop script
│
├── templates/                 # Web interface templates
│   └── index.html            # Main web interface
│
├── static/                    # Static web assets (CSS, JS, images)
│
├── audio_files/              # Recording storage (gitignored)
│   ├── Channel_Name_1/       # Per-channel directories
│   │   ├── *.mp3            # Audio recordings
│   │   └── *_metadata.json  # Recording metadata
│   └── Channel_Name_2/
│
├── scripts/                   # Utility scripts
│   ├── cleanup_old_recordings.sh  # Automated cleanup script
│   ├── start_recording.sh         # Start recording daemon
│   ├── stop_recording.sh          # Stop recording daemon
│   └── start-dev.sh              # Development startup script
│
├── docs/                      # Documentation
│   ├── API.md                # API documentation
│   ├── ARCHITECTURE.md       # System architecture
│   ├── CLEANUP_GUIDE.md      # Cleanup procedures
│   ├── CONFIGURATION.md      # Configuration guide
│   ├── INSTALLATION.md       # Installation instructions
│   └── RECORDING_GUIDE.md    # Recording operations guide
│
├── dev/                       # Development and testing tools
│   ├── test_*.py             # Unit tests and test scripts
│   ├── test_*.html           # Frontend testing pages
│   ├── debug_*.py            # Debugging utilities
│   ├── debug_*.html          # Debug interfaces
│   ├── channel_health_monitor.py  # Channel monitoring
│   ├── cleanup_temp.py       # Temp file cleanup utility
│   └── quick_start.py        # Quick development setup
│
├── tests/                     # Formal test suite
│   └── test_app.py           # Application tests
│
└── logs/                      # Log files (created at runtime)
    ├── recording.log         # Recording operations
    ├── cleanup.log           # Cleanup operations
    └── flask.log             # Web application logs
```

## Core Files

### Main Application Files

**`main.py`**
- Flask web application
- REST API endpoints
- Static file serving
- Web interface routes

**`audio_recorder.py`**
- Core audio recording engine
- Multi-channel stream management
- Transmission detection algorithm
- File processing and cleanup
- Background maintenance tasks

**`config.py`**
- Configuration management
- Settings validation
- Default values

**`start_recording.py`**
- Standalone recording script
- Starts recording for all configured channels
- Command-line interface for background recording
- Signal handling for graceful shutdown

**`stop_recording.py`**
- Standalone stop script
- Stops recording via API or process termination
- Process management and cleanup
- Graceful shutdown handling

**`radio_channels.json`**
- Channel definitions and settings
- Stream URLs and parameters
- Per-channel configuration overrides

### Web Interface

**`templates/index.html`**
- Main web interface
- Channel status table
- Recording modal with playback
- Batch selection and time filtering
- Real-time status updates

**`static/`** (Directory for static assets)
- CSS stylesheets
- JavaScript files
- Images and icons
- Audio player assets

## Utility Scripts

### `scripts/cleanup_old_recordings.sh`
- Removes recordings older than 7 days
- Designed for cron automation
- Comprehensive logging
- Safe file operations

### `scripts/start_recording.sh` & `scripts/stop_recording.sh`
- Daemon management scripts
- Process control utilities
- System service integration

### `scripts/start-dev.sh`
- Development environment setup
- Debug mode configuration
- Development server startup

## Documentation

### User Documentation
- **`README.md`**: Project overview and quick start
- **`docs/INSTALLATION.md`**: Detailed installation guide
- **`docs/CONFIGURATION.md`**: Configuration options and tuning
- **`docs/RECORDING_GUIDE.md`**: Recording operations and troubleshooting

### Technical Documentation
- **`docs/API.md`**: REST API reference
- **`docs/ARCHITECTURE.md`**: System design and architecture
- **`docs/CLEANUP_GUIDE.md`**: File management and cleanup procedures

## Development Tools

### Testing and Debugging
- **`dev/test_*.py`**: Unit tests for various components
- **`dev/test_*.html`**: Frontend testing interfaces
- **`dev/debug_*.py`**: Debugging utilities and tools
- **`dev/debug_*.html`**: Debug web interfaces

### Utilities
- **`dev/channel_health_monitor.py`**: Channel connectivity monitoring
- **`dev/cleanup_temp.py`**: Manual temp file cleanup
- **`dev/quick_start.py`**: Quick development environment setup

### Test Pages
- **`dev/test_api.html`**: API endpoint testing
- **`dev/test_audio.html`**: Audio playback testing
- **`dev/test_modal.html`**: Modal interface testing
- **`dev/test_format.html`**: Audio format testing

## Runtime Files

### Log Files (Created at Runtime)
- **`recording.log`**: Audio recording operations and errors
- **`cleanup.log`**: File cleanup operations and statistics
- **`flask.log`**: Web application access and error logs

### Audio Storage
- **`audio_files/`**: Root directory for recordings
- **`audio_files/{Channel_Name}/`**: Per-channel subdirectories
- **`*.mp3`**: Audio recording files
- **`*_metadata.json`**: Recording metadata and information
- **`temp_*.mp3`**: Temporary files during processing

## Configuration Files

### Python Environment
- **`pyproject.toml`**: Project metadata, dependencies, and build configuration
- **`uv.lock`**: Locked dependency versions for reproducible builds
- **`.python-version`**: Python version specification
- **`.venv/`**: Virtual environment (created by UV, gitignored)
- **`.gitignore`**: Git ignore patterns for generated files

### Package Management (UV)
This project uses [UV](https://docs.astral.sh/uv/) for fast, reliable Python package management:
- **Automatic virtual environment management**: UV creates and manages `.venv/`
- **Lock file for reproducibility**: `uv.lock` ensures consistent builds
- **Fast dependency resolution**: Rust-based resolver for quick installs
- **All scripts use `uv run`**: Ensures proper environment activation

### Application Configuration
- **`radio_channels.json`**: Channel definitions and settings
- **Environment variables**: Runtime configuration overrides

## File Naming Conventions

### Audio Files
- **Recording format**: `YYYYMMDD_HHMMSS_mmm_ChannelName.mp3`
- **Metadata format**: `YYYYMMDD_HHMMSS_mmm_ChannelName_metadata.json`
- **Temporary format**: `temp_YYYYMMDD_HHMMSS_mmm_ChannelName.mp3`

### Log Files
- **Application logs**: Use `.log` extension
- **Timestamped entries**: ISO 8601 format with timezone
- **Structured format**: Level, timestamp, component, message

## Permissions and Security

### File Permissions
- **Executable scripts**: `755` (rwxr-xr-x)
- **Configuration files**: `644` (rw-r--r--)
- **Audio files**: `644` (rw-r--r--)
- **Log files**: `644` (rw-r--r--)

### Directory Permissions
- **Application directories**: `755` (rwxr-xr-x)
- **Audio storage**: `755` (rwxr-xr-x)
- **Log directory**: `755` (rwxr-xr-x)

## Maintenance

### Regular Cleanup
- **Temporary files**: Automatic cleanup every hour
- **Old recordings**: Configurable retention (default 7 days)
- **Log rotation**: Manual or via system tools
- **Orphaned files**: Automatic detection and removal

### Backup Recommendations
- **Configuration files**: `radio_channels.json`, `pyproject.toml`
- **Important recordings**: Copy before automated cleanup
- **System logs**: For troubleshooting and analysis
- **Custom modifications**: Any local changes to core files

## Development Workflow

### Adding New Features
1. Implement in appropriate core file (`main.py` or `audio_recorder.py`)
2. Add tests in `dev/test_*.py`
3. Update documentation in `docs/`
4. Test with development tools in `dev/`

### Testing Changes
1. Use `dev/quick_start.py` for rapid testing
2. Run specific tests in `dev/`
3. Test with debug interfaces
4. Validate with production-like data

### Deployment
1. Update documentation
2. Test with `scripts/start-dev.sh`
3. Use `scripts/` for production deployment
4. Monitor logs for issues

This organized structure provides clear separation of concerns, making the project easier to maintain, test, and extend while keeping development tools and documentation easily accessible.
