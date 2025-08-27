# Installation and Setup Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu/Debian recommended), macOS, or Windows with WSL
- **Python**: 3.11 or higher
- **Storage**: At least 10GB free space (more recommended for recordings)
- **Network**: Stable internet connection for radio streams
- **Memory**: Minimum 2GB RAM (4GB+ recommended for multiple channels)

### Required Software

#### FFmpeg
FFmpeg is required for audio processing.

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows (WSL):**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### UV Package Manager
This project uses UV for dependency management.

**Install UV:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or visit [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/) for other methods.

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd stream_recorder
```

### 2. Install Dependencies
```bash
uv sync
```

This will create a virtual environment and install all required packages.

### 3. Verify Installation
```bash
uv run python -c "import pydub; print('Dependencies installed successfully')"
```

## Configuration

### 1. Channel Configuration
Edit `radio_channels.json` to configure your radio channels:

```json
{
  "Channel_ID": {
    "name": "Display Name",
    "stream_url": "http://stream.url/mount",
    "silence_threshold": -50,
    "silence_gap": 2.0,
    "min_transmission_length": 1.0,
    "max_transmission_length": 300.0
  }
}
```

**Parameter Descriptions:**
- `name`: Friendly name displayed in web interface
- `stream_url`: Direct URL to audio stream (MP3/AAC)
- `silence_threshold`: dB level below which audio is considered silence (-60 to -30)
- `silence_gap`: Seconds of silence that end a transmission (1.0 to 5.0)
- `min_transmission_length`: Minimum recording duration in seconds
- `max_transmission_length`: Maximum recording duration in seconds

### 2. Audio Settings
Key settings in `audio_recorder.py`:

```python
# Global detection settings
SILENCE_THRESHOLD = -45        # Default silence threshold (dB)
SILENCE_GAP = 2.0             # Default silence gap (seconds)
MIN_TRANSMISSION_LENGTH = 2.0  # Minimum transmission duration
MAX_TRANSMISSION_LENGTH = 300.0 # Maximum transmission duration

# Processing settings
CHUNK_SIZE = 1024             # Audio processing chunk size
SAMPLE_RATE = 22050           # Audio sample rate
CHANNELS = 1                  # Mono audio
```

### 3. Storage Configuration
By default, recordings are stored in `audio_files/`. To change:

1. Update the `AUDIO_DIR` variable in `audio_recorder.py`
2. Ensure the directory has write permissions
3. Consider storage space requirements (roughly 1MB per minute of audio)

## Running the Application

### Development Mode
```bash
uv run python main.py
```

The application will start with:
- Web interface at: http://localhost:8000
- Debug mode enabled
- Auto-reload on code changes

### Production Mode
For production deployment, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
uv add gunicorn

# Run with Gunicorn
uv run gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Background Service
To run as a system service, create a systemd service file:

```ini
# /etc/systemd/system/stream-recorder.service
[Unit]
Description=Radio Stream Recorder
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/stream_recorder
Environment=PATH=/path/to/.local/bin
ExecStart=/home/your-username/.local/bin/uv run python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable stream-recorder
sudo systemctl start stream-recorder
```

## Network Configuration

### Firewall Settings
If running on a server, open the required port:

```bash
# Ubuntu/Debian
sudo ufw allow 8000

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### Reverse Proxy (Optional)
For production, consider using Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /api/recording/ {
        proxy_pass http://localhost:8000;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## Automated Cleanup

### Temporary Files
Temp files are automatically cleaned up, but you can also set up manual cleanup:

```bash
# Make cleanup script executable
chmod +x scripts/cleanup_old_recordings.sh

# Add to crontab for daily cleanup at 2 AM
crontab -e
# Add this line:
0 2 * * * /path/to/stream_recorder/scripts/cleanup_old_recordings.sh
```

### Recording Retention
The cleanup script removes recordings older than 7 days. To modify:

1. Edit `scripts/cleanup_old_recordings.sh`
2. Change the `DAYS_OLD` variable
3. Restart the cron job

## Troubleshooting

### Common Issues

#### "FFmpeg not found"
```bash
# Verify FFmpeg installation
ffmpeg -version

# Install if missing
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

#### "Permission denied" errors
```bash
# Fix audio_files directory permissions
chmod 755 audio_files
chmod 644 audio_files/*

# Fix script permissions
chmod +x scripts/*.sh
```

#### "Stream connection failed"
1. Verify stream URLs are accessible
2. Check network connectivity
3. Test with curl:
   ```bash
   curl -I "http://stream.url/mount"
   ```

#### High CPU usage
1. Reduce number of active channels
2. Increase `CHUNK_SIZE` in audio_recorder.py
3. Lower `SAMPLE_RATE` if quality permits

#### Storage issues
1. Monitor disk space: `df -h`
2. Set up automated cleanup
3. Consider external storage for recordings

### Log Files
Check log files for detailed error information:
- `recording.log`: Recording operations
- `cleanup.log`: Cleanup operations
- `flask.log`: Web application logs

### Testing Installation
Run the test suite to verify everything works:

```bash
cd dev/
uv run python test_channels.py
uv run python test_voice_detection.py
```

## Performance Optimization

### For High Channel Counts
- Increase system file descriptor limits
- Use SSD storage for better I/O
- Consider multiple application instances

### For Long-term Operation
- Set up log rotation
- Monitor memory usage
- Implement health checks

## Security Considerations

### Network Security
- Run behind a firewall
- Use VPN for remote access
- Consider authentication for web interface

### File System Security
- Run with minimal privileges
- Secure audio file storage
- Regular backup of recordings

## Updates and Maintenance

### Updating Dependencies
```bash
uv sync --upgrade
```

### Backing Up Configuration
```bash
# Backup important files
cp radio_channels.json radio_channels.json.backup
cp -r audio_files audio_files.backup
```

### Monitoring
Set up monitoring for:
- Disk space usage
- Application uptime
- Recording success rates
- Network connectivity
