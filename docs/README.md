# Stream Recorder Documentation

## Quick Start

1. **[README.md](../README.md)** - Main project documentation and setup
2. **[Volume Sensitivity Guide](VOLUME_SENSITIVITY_GUIDE.md)** - Complete guide to configuring audio detection
3. **[Simplification Summary](SIMPLIFICATION_SUMMARY.md)** - Overview of recent system changes

## Core Documentation

### Configuration
- **[Volume Sensitivity Guide](VOLUME_SENSITIVITY_GUIDE.md)** - Detailed tuning guide
- **[Configuration](CONFIGURATION.md)** - General configuration options
- **[Recording Guide](RECORDING_GUIDE.md)** - Recording setup and management

### Technical Details
- **[Simplification Summary](SIMPLIFICATION_SUMMARY.md)** - System architecture changes
- **[FLAC Support](FLAC_SUPPORT_UPDATE.md)** - Audio format details
- **[MP3 to FLAC Migration](MP3_TO_FLAC_MIGRATION.md)** - Format migration guide
- **[Project Cleanup Summary](PROJECT_CLEANUP_SUMMARY.md)** - Recent reorganization details

## Development

### Scripts and Tools
- **[Scripts README](../scripts/README.md)** - Available scripts and utilities
- **[Dev Tools](../dev/README.md)** - Development and testing tools

### Testing
- **[Test Configuration](TEST_CONFIGURATION.md)** - Testing setup and procedures

## Legacy Documentation

The `legacy/` directory contains documentation from previous versions:
- Audio improvements and optimizations
- Cleanup procedures and scripts
- Refactoring summaries
- Transmission analysis reports

## Common Tasks

### Setting Up Audio Detection
1. Read [Volume Sensitivity Guide](VOLUME_SENSITIVITY_GUIDE.md)
2. Configure `volume_sensitivity` in `radio_channels.json`
3. Test and tune based on results

### Adding New Channels
1. Add channel to `radio_channels.json`
2. Set appropriate `volume_sensitivity` (start with 0.01)
3. Test and adjust as needed

### Troubleshooting
1. Check [Volume Sensitivity Guide](VOLUME_SENSITIVITY_GUIDE.md) troubleshooting section
2. Review log files for RMS values and detection patterns
3. Use dev tools for channel testing

### File Management
1. Recordings saved as FLAC files in `audio_files/`
2. Temporary files automatically cleaned up
3. Use scripts for bulk operations

## Support

For issues:
1. Check relevant documentation above
2. Review log files for errors
3. Use development tools for debugging
4. Check [README.md](../README.md) for general troubleshooting

---

*Last updated: January 2025*
