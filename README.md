# Radio Stream Recorder

A comprehensive Python application for recording and managing radio transmissions from multiple channels simultaneously.

## Features

- **Multi-Channel Recording**: Record from up to 25+ radio channels simultaneously
- **Advanced Audio Processing**: Professional VAD, filtering, and real-time transmission detection
- **High-Quality Audio**: FLAC archival format with lossless quality preservation
- **Modern Format Support**: Full FLAC and MP3 playback support in web interface
- **Intelligent Transmission Detection**: Frame-based VAD with hysteresis and pre-roll buffering
- **Web Interface**: Modern web UI for monitoring channels and managing recordings
- **Automatic Cleanup**: Built-in temp file cleanup and configurable retention policies
- **Real-time Monitoring**: Live status updates and channel health monitoring
- **Batch Playback**: Select and play multiple recordings in sequence
- **Time-based Filtering**: Filter recordings by date and time ranges
- **Per-Channel Configuration**: Customize audio processing settings for each channel
- **Cross-Browser Compatibility**: FLAC playback support across modern browsers

## Quick Start

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Start the Application**:
   ```bash
   uv run python main.py
   ```

3. **Access Web Interface**:
   Open http://localhost:8000 in your browser

## Project Structure

```
stream_recorder/
├── main.py                 # Main Flask application
├── audio_recorder.py       # Core recording engine
├── audio_manager.py        # Audio processing utilities
├── config.py              # Configuration management
├── radio_channels.json    # Channel definitions
├── templates/             # Web interface templates
├── static/               # Static web assets
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── dev/                  # Development/testing tools
└── audio_files/          # Recorded audio storage
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
- Multi-channel audio streaming
- Transmission detection and filtering
- Audio file processing with FFmpeg
- Automatic cleanup and maintenance

### Configuration (`radio_channels.json`)
Defines radio channels with:
- Channel names and identifiers
- Stream URLs and audio parameters
- Detection thresholds and settings

## Usage

### Web Interface
- Browse channels in the main table
- Click channel names to view recordings
- Use date/time filters to find specific recordings
- Select multiple recordings for batch playback
- Monitor real-time recording status
- **FLAC and MP3 playback**: Modern browsers support high-quality FLAC audio natively

### Audio Quality & Formats
- **FLAC files**: New recordings use lossless FLAC format with rich metadata
- **MP3 files**: Legacy recordings remain accessible
- **Advanced processing**: Voice Activity Detection, filtering, and noise reduction
- **Browser compatibility**: Automatic format detection and fallback support

### API Endpoints
- `GET /api/channels` - List all channels
- `GET /api/recordings/channel/{name}` - Get channel recordings
- `GET /api/status` - System status
- `POST /api/cleanup-temp` - Manual cleanup
- `GET /api/cleanup-status` - Cleanup statistics

### Command Line Scripts
- `scripts/cleanup_old_recordings.sh` - Remove old recordings (7+ days)
- `scripts/start_recording.sh` - Start recording daemon
- `scripts/stop_recording.sh` - Stop recording daemon

## Configuration

### Channel Setup
Edit `radio_channels.json` to add/modify channels:
```json
{
  "Channel_Name": {
    "name": "Friendly Name",
    "stream_url": "http://stream.url/path",
    "silence_threshold": -50,
    "silence_gap": 2.0
  }
}
```

### Audio Settings
Key parameters in `audio_recorder.py`:
- `SILENCE_THRESHOLD`: dB level for silence detection
- `SILENCE_GAP`: seconds of silence between transmissions
- `MIN_TRANSMISSION_LENGTH`: minimum recording duration
- `MAX_TRANSMISSION_LENGTH`: maximum recording duration

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
python test_channels.py
python test_voice_detection.py
```

### Debug Tools
- `dev/debug_recording.py` - Audio processing debugging
- `dev/test_*.html` - Frontend component testing
- `dev/channel_health_monitor.py` - Channel monitoring utilities

## Requirements

- Python 3.11+
- FFmpeg (for audio processing)
- Network access to radio stream URLs
- Sufficient storage for audio files

## Dependencies

See `pyproject.toml` for complete dependency list. Key packages:
- Flask (web framework)
- pydub (audio processing)
- requests (HTTP client)
- threading (concurrent processing)

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