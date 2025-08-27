# Configuration Guide

## Overview

This guide covers all configuration options for the Radio Stream Recorder.

## Channel Configuration

### Basic Channel Setup

Edit `radio_channels.json` to define your radio channels:

```json
{
  "2_-_Sheriff": {
    "name": "County Sheriff",
    "stream_url": "http://scanner.example.com:8000/sheriff",
    "silence_threshold": -45,
    "silence_gap": 2.0,
    "min_transmission_length": 2.0,
    "max_transmission_length": 300.0
  },
  "Fire_Dept": {
    "name": "Fire Department",
    "stream_url": "http://scanner.example.com:8000/fire",
    "silence_threshold": -50,
    "silence_gap": 1.5,
    "min_transmission_length": 1.0,
    "max_transmission_length": 180.0
  }
}
```

### Channel Parameters

#### Required Parameters

**name** (string)
- Display name shown in web interface
- Keep concise but descriptive
- Example: "County Sheriff", "Fire Dispatch"

**stream_url** (string)
- Direct URL to audio stream
- Must be accessible HTTP/HTTPS stream
- Supported formats: MP3, AAC
- Example: `http://scanner.example.com:8000/mount`

#### Optional Parameters

**silence_threshold** (number, default: -45)
- Audio level in dB below which sound is considered silence
- Range: -60 to -30
- Lower values = more sensitive (picks up quieter audio)
- Higher values = less sensitive (ignores background noise)
- Typical values:
  - Clean streams: -50 to -45
  - Noisy streams: -40 to -35
  - Very quiet streams: -55 to -50

**silence_gap** (number, default: 2.0)
- Seconds of continuous silence that end a transmission
- Range: 0.5 to 5.0
- Lower values = captures rapid-fire conversations
- Higher values = avoids splitting single transmissions
- Typical values:
  - Fast-paced channels: 1.0 to 1.5
  - Normal channels: 2.0 to 2.5
  - Slow channels: 3.0 to 4.0

**min_transmission_length** (number, default: 2.0)
- Minimum duration in seconds to save a recording
- Range: 0.5 to 10.0
- Filters out brief noise or false triggers
- Typical values:
  - Strict filtering: 3.0 to 5.0
  - Normal filtering: 2.0 to 3.0
  - Capture everything: 1.0 to 2.0

**max_transmission_length** (number, default: 300.0)
- Maximum duration in seconds for a single recording
- Range: 30.0 to 600.0
- Prevents runaway recordings from system issues
- Typical values: 180.0 to 300.0

### Channel Tuning

#### Finding the Right Settings

1. **Start with defaults** and monitor results
2. **Adjust silence_threshold** if missing/capturing too much
3. **Tune silence_gap** for conversation patterns
4. **Set min_transmission_length** to filter noise
5. **Use debug tools** to visualize audio levels

#### Example Configurations

**High-traffic emergency channel:**
```json
{
  "name": "Emergency Dispatch",
  "stream_url": "http://scanner.example.com:8000/emergency",
  "silence_threshold": -40,
  "silence_gap": 1.0,
  "min_transmission_length": 1.5,
  "max_transmission_length": 120.0
}
```

**Low-traffic administrative channel:**
```json
{
  "name": "Admin Channel",
  "stream_url": "http://scanner.example.com:8000/admin",
  "silence_threshold": -50,
  "silence_gap": 3.0,
  "min_transmission_length": 3.0,
  "max_transmission_length": 600.0
}
```

**Noisy/poor quality stream:**
```json
{
  "name": "Backup Channel",
  "stream_url": "http://scanner.example.com:8000/backup",
  "silence_threshold": -35,
  "silence_gap": 2.5,
  "min_transmission_length": 4.0,
  "max_transmission_length": 300.0
}
```

## Application Configuration

### Audio Processing Settings

Edit `audio_recorder.py` for global audio settings:

```python
# Audio processing parameters
CHUNK_SIZE = 1024              # Buffer size (lower = more responsive, higher = more efficient)
SAMPLE_RATE = 22050           # Audio quality (22050 = good balance, 44100 = higher quality)
CHANNELS = 1                  # Always 1 for mono radio streams
FORMAT = pyaudio.paFloat32    # Audio format (don't change)

# Detection defaults (overridden by channel config)
SILENCE_THRESHOLD = -45       # Default silence threshold
SILENCE_GAP = 2.0            # Default silence gap
MIN_TRANSMISSION_LENGTH = 2.0 # Default minimum length
MAX_TRANSMISSION_LENGTH = 300.0 # Default maximum length

# File management
TEMP_FILE_MAX_AGE = 3600     # Seconds before temp files are cleaned up
CLEANUP_INTERVAL = 3600      # Seconds between automatic cleanups
```

### Web Interface Settings

Edit `main.py` for web application settings:

```python
# Flask application settings
DEBUG = True                  # Set to False for production
HOST = '0.0.0.0'             # Listen on all interfaces
PORT = 8000                  # Web interface port
THREADED = True              # Enable threading for concurrent requests

# CORS settings (for cross-origin requests)
CORS_ORIGINS = ['*']         # Allowed origins (* = all, or specify domains)

# File serving
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # Max file size (500MB)
SEND_FILE_MAX_AGE = 31536000             # Cache duration for static files
```

### Logging Configuration

Configure logging levels and outputs:

```python
# In main.py or audio_recorder.py
import logging

# Set logging level
logging.basicConfig(
    level=logging.INFO,        # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recording.log'),
        logging.StreamHandler()  # Also log to console
    ]
)

# Specific logger levels
logging.getLogger('audio_recorder').setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reduce Flask noise
```

## Storage Configuration

### Directory Structure

The default structure can be customized:

```python
# In audio_recorder.py
AUDIO_DIR = "audio_files"     # Base directory for recordings
TEMP_PREFIX = "temp_"         # Prefix for temporary files
```

### File Naming

Recordings follow this pattern:
```
YYYYMMDD_HHMMSS_mmm_ChannelName.mp3
```

Example: `20250826_140530_123_2_-_Sheriff.mp3`
- Date: 2025-08-26
- Time: 14:05:30.123
- Channel: 2_-_Sheriff

### Storage Management

Configure automatic cleanup in `scripts/cleanup_old_recordings.sh`:

```bash
# Retention period
DAYS_OLD=7                    # Keep recordings for 7 days

# Directories to clean
AUDIO_DIR="$SCRIPT_DIR/audio_files"

# File types to remove
find "$AUDIO_DIR" -type f -name "*.mp3" -mtime +$DAYS_OLD
find "$AUDIO_DIR" -type f -name "*_metadata.json" -mtime +$DAYS_OLD
```

## Advanced Configuration

### Multiple Application Instances

Run multiple instances for load balancing:

```bash
# Instance 1 - channels 1-10
uv run python main.py --port 8000 --channels 1-10

# Instance 2 - channels 11-20  
uv run python main.py --port 8001 --channels 11-20
```

### Custom Audio Processing

Override audio processing functions:

```python
# In audio_recorder.py
def custom_transmission_detector(audio_data, threshold):
    """Custom transmission detection logic"""
    # Your implementation here
    return is_transmission, audio_level

def custom_audio_filter(audio_data):
    """Custom audio filtering/enhancement"""
    # Your implementation here
    return filtered_audio
```

### External Integration

Configure webhooks or external notifications:

```python
# In audio_recorder.py
def on_transmission_recorded(channel, filename, duration):
    """Called when a transmission is recorded"""
    # Send webhook, update database, etc.
    webhook_url = "http://your.api.com/webhook"
    data = {
        "channel": channel,
        "filename": filename,
        "duration": duration,
        "timestamp": datetime.now().isoformat()
    }
    requests.post(webhook_url, json=data)
```

## Environment Variables

Use environment variables for sensitive or deployment-specific settings:

```bash
# .env file
STREAM_RECORDER_DEBUG=false
STREAM_RECORDER_HOST=0.0.0.0
STREAM_RECORDER_PORT=8000
STREAM_RECORDER_LOG_LEVEL=INFO
AUDIO_BASE_DIR=/mnt/recordings
```

Load in application:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('STREAM_RECORDER_DEBUG', 'true').lower() == 'true'
HOST = os.getenv('STREAM_RECORDER_HOST', '0.0.0.0')
PORT = int(os.getenv('STREAM_RECORDER_PORT', '8000'))
```

## Testing Configuration

Use the development tools to test settings:

```bash
# Test channel connectivity
cd dev/
uv run python test_channels.py

# Test audio detection settings
uv run python test_voice_detection.py

# Test with specific channel
uv run python debug_recording.py --channel "2_-_Sheriff"
```

## Configuration Validation

The application validates configuration on startup:

- Stream URLs are accessible
- Audio parameters are within valid ranges
- Required directories exist and are writable
- FFmpeg is available and functional

Check logs for validation errors:
```bash
tail -f recording.log | grep -i error
```

## Best Practices

### Channel Management
- Use descriptive but concise channel names
- Group related channels with consistent naming
- Test new channels individually before adding to production

### Performance Optimization
- Monitor CPU and memory usage with many channels
- Adjust `CHUNK_SIZE` for performance/responsiveness balance
- Use appropriate `SAMPLE_RATE` for quality/storage balance

### Maintenance
- Regularly review and tune channel settings
- Monitor storage usage and cleanup effectiveness
- Keep configuration backups
- Document any custom modifications

### Security
- Restrict network access to application
- Use environment variables for sensitive settings
- Regular security updates of dependencies
- Monitor for unusual activity or errors
