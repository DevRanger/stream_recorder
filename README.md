# Radio Stream Recorder

A comprehensive Python application for recording and managing radio transmissions from multiple channels simultaneously with advanced audio processing and web interface.

## Features

- **Multi-Channel Recording**: Record from 25+ radio channels simultaneously
- **High-Quality Audio**: MP3 format with advanced audio processing
- **Intelligent Voice Detection**: Smart transmission detection with configurable silence gaps
- **Web Interface**: Modern web UI for monitoring channels and managing recordings
- **Automatic Cleanup**: Built-in temp file cleanup and configurable retention policies
- **Batch Playback**: Select and play multiple recordings in sequence
- **Time-based Filtering**: Filter recordings by date and time ranges
- **Per-Channel Configuration**: Customize volume sensitivity for each channel
- **Cross-Browser Compatibility**: Reliable audio playback across modern browsers
- **Real-time Monitoring**: Live channel status and recording activity

## Quick Start

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Start Recording**:
   ```bash
   ./start_recording.py
   ```

3. **Start Web Interface**:
   ```bash
   uv run python main.py
   ```

4. **Access Web Interface**:
   Open http://localhost:8000 in your browser

## Recent Improvements

- **Enhanced Voice Detection**: Configurable 4-second silence gap prevents premature recording stops
- **Project Cleanup**: Removed redundant files and organized codebase
- **Improved Documentation**: Comprehensive docs in `docs/` directory
- **Better Testing**: Organized test suite in `dev/` and `tests/` directories
- **Streamlined Configuration**: Simplified channel setup with volume sensitivity controls

## Project Structure

```
stream_recorder/
├── main.py                 # Main Flask web application
├── audio_recorder.py       # Core recording engine with audio processing
├── radio_channels.json     # Channel configuration and settings
├── start_recording.py      # Recording daemon control
├── stop_recording.py       # Stop recording processes
├── templates/              # Web interface templates
├── static/                 # Static web assets (CSS, JS)
├── scripts/                # Utility and cleanup scripts
├── docs/                   # Complete documentation
├── dev/                    # Development and testing tools
├── tests/                  # Unit tests
├── archive/                # Historical files and legacy code
└── audio_files/            # Recorded audio storage (organized by channel)
```

## Core Components

### Main Application (`main.py`)
Flask web application providing:
- REST API endpoints for channel management
- Recording playback and download
- Cleanup operations and status monitoring
- Web interface serving

### Audio Recording Engine (`audio_recorder.py`)
Handles:
- Multi-channel audio streaming with concurrent processing
- Voice activity detection and transmission filtering
- Audio file processing and metadata creation
- Automatic cleanup and maintenance
- Per-channel volume sensitivity configuration
- Configurable silence gaps (currently 4 seconds)

### Configuration (`radio_channels.json`)
Defines radio channels with:
- Channel names and stream URLs
- Enable/disable flags for selective recording
- Channel grouping for organization
- Volume sensitivity settings per channel

## Usage

### Web Interface
- Browse channels in the main table
- Click channel names to view recordings
- Use date/time filters to find specific recordings
- Select multiple recordings for batch playback
- Monitor real-time recording status
- **MP3 audio playback**: Reliable streaming across all browsers

### Audio Quality & Processing
- **MP3 format**: Optimized for web streaming and storage efficiency
- **Voice Activity Detection**: Smart detection of actual transmissions
- **Configurable silence gaps**: 4-second silence detection prevents false stops
- **Volume sensitivity**: Per-channel sensitivity tuning
- **Automatic filtering**: Removes background noise and short clips

### API Endpoints
- `GET /api/channels` - List all channels
- `GET /api/recordings/channel/{name}` - Get channel recordings
- `GET /api/status` - System status
- `POST /api/cleanup-temp` - Manual cleanup
- `GET /api/cleanup-status` - Cleanup statistics

### Command Line Scripts
- `./start_recording.py` - Start recording daemon for all enabled channels
- `./stop_recording.py` - Stop recording daemon and all processes
- `cleanup_old_recordings.sh` - Remove old recordings (configurable retention)
- `cleanup_temp.py` - Clean up temporary audio files

## Configuration

### Channel Setup
Edit `radio_channels.json` to add/modify channels:
```json
{
  "channels": [
    {
      "name": "Channel Name",
      "url": "https://stream.url/path",
      "enabled": true,
      "group": "Category",
      "volume_sensitivity": 0.01
    }
  ]
}
```

### Audio Settings
Key parameters in `audio_recorder.py`:
- `silence_gap`: 4000ms (4 seconds of silence before stopping recording)
- `min_transmission_length`: 500ms (minimum recording duration)
- `max_transmission_length`: 45000ms (maximum recording duration)
- `volume_sensitivity`: Per-channel sensitivity (in radio_channels.json)

## Automated Maintenance

### Temp File Cleanup
- **Startup**: Removes old temp files on application start
- **Background**: Hourly cleanup of orphaned temp files
- **Post-processing**: Immediate cleanup after transmission extraction

### Recording Retention
Set up automated cleanup with cron:
```bash
# Add to crontab for daily cleanup at 2 AM
0 2 * * * /path/to/stream_recorder/scripts/cleanup_old_recordings.sh
```

## Development

### Running Tests
```bash
cd dev/
uv run python test_channels.py
uv run python test_voice_detection.py
```

### Debug Tools
- `dev/debug_recording.py` - Audio processing debugging
- `dev/test_*.py` - Backend component testing
- `dev/test_*.html` - Frontend component testing
- `dev/channel_health_monitor.py` - Channel monitoring utilities

## Requirements

- Python 3.11+
- uv (Python package manager)
- FFmpeg (for audio processing)
- Network access to radio stream URLs
- Sufficient storage for audio files (MP3 format)

## Dependencies

See `pyproject.toml` for complete dependency list. Key packages:
- Flask (web framework)
- pydub (audio processing)
- requests (HTTP client)
- threading (concurrent processing)
- numpy (audio analysis)

## License

This project is for educational and personal use. Ensure compliance with radio stream terms of service and applicable laws.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## Support

For issues and questions:
1. Check the documentation in `docs/`
2. Review development tools in `dev/`
3. Examine log files for error details
4. Test with individual components first