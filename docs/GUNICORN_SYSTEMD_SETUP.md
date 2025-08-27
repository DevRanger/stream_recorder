# Gunicorn and Systemd Setup for Stream Recorder Web UI

This document describes the Gunicorn and systemd setup for running the Stream Recorder Web UI as a production service.

## Overview

The setup provides multiple ways to run the web UI:
1. **Manual Control** - Direct script execution
2. **Systemd Service** - System-managed service with auto-restart
3. **Development Mode** - Flask development server

## Files Created

### Configuration
- `gunicorn.conf.py` - Gunicorn configuration with production settings
- `stream-recorder-web.service` - Systemd service definition

### Scripts
- `scripts/start-web.sh` - Web UI control script (start/stop/status)
- `scripts/install-systemd-service.sh` - Systemd service installer

### Directories
- `logs/` - Gunicorn and application logs

## Manual Control (Recommended for Testing)

### Basic Usage
```bash
# Start web UI in foreground
./scripts/start-web.sh

# Start web UI in background (daemon)
./scripts/start-web.sh --background

# Stop web UI
./scripts/start-web.sh --stop

# Check status
./scripts/start-web.sh --status
```

### Using Master Control Script
```bash
# Start web UI in background
./recorder.sh web --background

# Stop web UI
./recorder.sh web-stop

# Check status
./recorder.sh web-status
```

## Systemd Service Setup

### 1. Install the Service
```bash
# Run the installer (will prompt for sudo when needed)
./scripts/install-systemd-service.sh
```

### 2. Enable and Start Service
```bash
# Enable auto-start on boot
sudo systemctl enable stream-recorder-web

# Start the service
sudo systemctl start stream-recorder-web

# Check status
sudo systemctl status stream-recorder-web
```

### 3. Service Management
```bash
# Start service
sudo systemctl start stream-recorder-web

# Stop service
sudo systemctl stop stream-recorder-web

# Restart service
sudo systemctl restart stream-recorder-web

# Reload configuration (graceful restart)
sudo systemctl reload stream-recorder-web

# Check status
sudo systemctl status stream-recorder-web

# View logs
sudo journalctl -u stream-recorder-web -f
```

## Configuration Details

### Gunicorn Configuration (`gunicorn.conf.py`)
- **Bind**: `0.0.0.0:8000` (accessible from all interfaces)
- **Workers**: Auto-scaled based on CPU cores
- **Logging**: Separate access and error logs
- **Security**: Process isolation and resource limits
- **Restart**: Workers restart after 1000 requests to prevent memory leaks

### Systemd Service Features
- **Auto-restart**: Service restarts on failure
- **Security**: Restricted filesystem access and privileges
- **Resource limits**: File descriptor and process limits
- **Logging**: Integrated with systemd journal

## Access and URLs

### Web Interface
- **URL**: http://localhost:8000
- **Development**: http://localhost:8000 (Flask dev server via `./recorder.sh dev`)

### Log Files
- **Gunicorn Access**: `logs/gunicorn_access.log`
- **Gunicorn Error**: `logs/gunicorn_error.log`
- **Systemd Journal**: `sudo journalctl -u stream-recorder-web`

## Security Considerations

### File Permissions
- Service runs as user `daryl`
- Restricted read/write access to project directories only
- No new privileges allowed

### Network Security
- Binds to all interfaces (0.0.0.0) - consider firewall rules
- No SSL/TLS by default - use reverse proxy for HTTPS

### Recommendations
1. Use reverse proxy (nginx) for HTTPS and additional security
2. Configure firewall to restrict access to port 8000
3. Regular log rotation and monitoring
4. Keep dependencies updated

## Troubleshooting

### Service Won't Start
```bash
# Check service status
sudo systemctl status stream-recorder-web

# View detailed logs
sudo journalctl -u stream-recorder-web -n 50

# Check Gunicorn logs
tail -f logs/gunicorn_error.log
```

### Permission Issues
```bash
# Ensure proper ownership
sudo chown -R daryl:daryl /home/daryl/Python_Projects/stream_recorder

# Check file permissions
ls -la scripts/start-web.sh
ls -la gunicorn.conf.py
```

### Port Already in Use
```bash
# Find process using port 8000
sudo netstat -tulpn | grep :8000
sudo lsof -i :8000

# Kill conflicting process
sudo kill <PID>
```

### Dependencies Missing
```bash
# Update dependencies
cd /home/daryl/Python_Projects/stream_recorder
uv sync

# Verify Gunicorn is available
uv pip list | grep gunicorn
```

## Monitoring and Maintenance

### Health Checks
```bash
# Test web UI accessibility
curl -f http://localhost:8000 || echo "Web UI not accessible"

# Check process status
./recorder.sh web-status
```

### Log Rotation
Consider setting up log rotation for Gunicorn logs:
```bash
# Add to /etc/logrotate.d/stream-recorder-web
/home/daryl/Python_Projects/stream_recorder/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        sudo systemctl reload stream-recorder-web
    endscript
}
```

### Performance Monitoring
```bash
# Monitor resource usage
top -p $(cat logs/gunicorn.pid)

# Monitor worker processes
ps aux | grep gunicorn
```

## Integration with Recording Process

The web UI and recording process are independent:
- **Recording**: Use `./recorder.sh start --background` 
- **Web UI**: Use `./recorder.sh web --background`
- **Both**: Can run simultaneously and independently

This separation allows:
- Recording to continue if web UI crashes
- Web UI updates without affecting recording
- Independent scaling and resource management
