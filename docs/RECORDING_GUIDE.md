# Police Radio Audio Logger - Batch Recording Scripts

This document explains how to use the batch scripts to control recording independently from the web UI.

## Overview

The recording process has been isolated from the web UI. You can now:
- Start/stop recording using dedicated batch scripts
- Monitor recording status through the web UI (which no longer has control buttons)
- Keep recordings running independently of the web interface

## Batch Scripts

### Starting Recording

You can start recording for all channels using either:

**Shell script (recommended):**
```bash
# Run in foreground (will block terminal but show real-time status)
./start_recording.sh

# Run in background (returns immediately, logs to recording.log)
./start_recording.sh --background
```

**Python script:**
```bash
uv run python start_recording.py
```

**Background operation:**
```bash
# Start in background with nohup (survives terminal closure)
nohup ./start_recording.sh --background &
```

This will:
- Start recording for all 26 configured radio channels
- Create audio files in the `audio_files/` directory
- Show the list of channels being recorded
- Keep the recording process alive until manually stopped
- Log activity to `recording.log` (background mode only)

### Stopping Recording

You can stop recording for all active channels using either:

**Python script:**
```bash
uv run python stop_recording.py
```

**Shell script (recommended):**
```bash
./stop_recording.sh
```

This will:
- Stop recording for all currently active channels
- Find and terminate any background recording processes
- Show which channels were stopped
- Preserve all recorded audio files

**Note:** The stop script can find and stop both:
- Recording threads managed by AudioRecorder
- Background recording processes started with `--background`

### Monitoring Status

To monitor the recording status, start the web UI:

```bash
uv run python main.py
```

Then open http://127.0.0.1:8000 in your browser. The web interface will show:
- Current recording status for each channel (Recording/Idle)
- Channel information in a compact table format
- Access to recorded audio files and statistics

**Note:** The web UI no longer has start/stop buttons - it's read-only for monitoring purposes.

## File Organization

Recorded audio files are organized as follows:
```
audio_files/
├── 22_-_Redwood_City/
│   ├── 20250825_103829_125_22_-_Redwood_City.mp3
│   └── 20250825_104123_456_22_-_Redwood_City.mp3
├── CWMA/
│   └── 20250825_103830_789_CWMA.mp3
└── [other channels]/
```

## Process Isolation

The recording process runs independently from the web UI:
- **Persistent recording:** Process stays alive until explicitly stopped
- **Background operation:** Use `--background` flag to run without blocking terminal
- **Survives UI restarts:** You can restart the web UI without affecting recordings
- **Clean termination:** Stop script handles both foreground and background processes
- **Logging:** Background mode logs all activity to `recording.log`
- Each channel records to its own directory with timestamped filenames

## Tips

1. **Use background mode for production:** `./start_recording.sh --background`
2. **Monitor logs:** `tail -f recording.log` to see real-time activity
3. **Always use the stop script** before shutting down to ensure clean termination
4. **Monitor disk space** as continuous recording can generate large files
5. **Check logs** if recordings aren't starting - network issues can prevent stream connections
6. **Use the web UI** to browse and play back recorded audio files

## Troubleshooting

If recordings don't start:
- Check your internet connection
- Verify the radio stream URLs are accessible
- Look for error messages in the console output or `recording.log`
- Try starting individual channels to isolate issues

If the recording process stops unexpectedly:
- Check `recording.log` for error messages
- Look for network connectivity issues
- Verify sufficient disk space is available
- Restart with `./start_recording.sh --background`

If the web UI shows incorrect status:
- Refresh the page (click "Refresh Status" button)
- Restart the web server: `uv run python main.py`
- Check if recording processes are actually running: `ps aux | grep start_recording`
