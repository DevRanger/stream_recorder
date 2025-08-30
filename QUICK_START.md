# Quick Setup Guide

## New User Setup

### 1. Basic Configuration
```bash
# Clone or download the project
cd stream_recorder

# Install dependencies
uv sync

# Copy and configure channels
cp radio_channels.json radio_channels.json.backup
# Edit radio_channels.json with your channels and volume_sensitivity values
```

### 2. Volume Sensitivity Configuration

Start with these values in `radio_channels.json`:
```json
{
  "channels": [
    {
      "name": "Your Channel",
      "url": "https://stream.url/",
      "enabled": true,
      "group": "Police",
      "volume_sensitivity": 0.01
    }
  ]
}
```

### 3. Test and Tune

1. **Start recording**: `./scripts/start_recording.sh`
2. **Monitor logs**: `tail -f logs/recording.log`
3. **Check recordings**: Files appear in `audio_files/`
4. **Adjust sensitivity**: See [Volume Sensitivity Guide](docs/VOLUME_SENSITIVITY_GUIDE.md)

### 4. Web Interface

```bash
# Start web server
uv run python main.py

# Open browser to http://localhost:8000
```

## Quick Tuning Reference

| Problem | Solution |
|---------|----------|
| No recordings | Lower `volume_sensitivity` (try 0.005) |
| Too many short files | Raise `volume_sensitivity` (try 0.015) |
| Missing transmissions | Lower `volume_sensitivity` |
| Too much background noise | Raise `volume_sensitivity` |

## File Locations

- **Configuration**: `radio_channels.json`
- **Recordings**: `audio_files/[channel]/`
- **Logs**: `logs/recording.log`
- **Documentation**: `docs/`
- **Scripts**: `scripts/`

## Next Steps

1. Read [Volume Sensitivity Guide](docs/VOLUME_SENSITIVITY_GUIDE.md) for detailed tuning
2. Check [Documentation Index](docs/README.md) for all guides
3. Use development tools in `dev/` for testing

---

*For complete documentation, see [docs/README.md](docs/README.md)*
