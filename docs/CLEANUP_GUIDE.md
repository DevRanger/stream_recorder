# Audio Files Cleanup Script

## Overview
The `cleanup_old_recordings.sh` script automatically removes audio recordings and metadata files older than 7 days from the `audio_files` directory.

## Features
- Removes `.mp3` audio files older than 7 days
- Removes `*_metadata.json` files older than 7 days  
- Removes empty directories after cleanup
- Comprehensive logging with timestamps
- Safe operation - only removes files matching specific patterns
- Counts files before/after for reporting

## Manual Usage
```bash
cd /home/daryl/Python_Projects/stream_recorder
./cleanup_old_recordings.sh
```

## Automated Setup with Crontab

### 1. Edit your crontab:
```bash
crontab -e
```

### 2. Add one of these scheduling options:

**Daily at 2:00 AM (recommended):**
```cron
0 2 * * * /home/daryl/Python_Projects/stream_recorder/cleanup_old_recordings.sh
```

**Weekly on Sunday at 3:00 AM:**
```cron
0 3 * * 0 /home/daryl/Python_Projects/stream_recorder/cleanup_old_recordings.sh
```

**Every 3 days at 1:00 AM:**
```cron
0 1 */3 * * /home/daryl/Python_Projects/stream_recorder/cleanup_old_recordings.sh
```

### 3. Verify crontab entry:
```bash
crontab -l
```

## Log File
The script creates a log file at: `/home/daryl/Python_Projects/stream_recorder/cleanup.log`

You can monitor cleanup activity with:
```bash
tail -f /home/daryl/Python_Projects/stream_recorder/cleanup.log
```

## Configuration
To change the retention period, edit the `DAYS_OLD` variable in the script:
```bash
DAYS_OLD=7  # Change this number to adjust retention days
```

## Safety Features
- Only removes files in the `audio_files` directory
- Only targets `.mp3`, `.flac`, and `*_metadata.json` files
- Uses `-mtime +7` to ensure files are actually older than 7 full days
- Comprehensive logging of all actions
- Graceful error handling

## Example Log Output
```
2025-08-26 18:38:50 - Starting cleanup of audio files older than 7 days
2025-08-26 18:38:50 - Total audio files before cleanup: 4269
2025-08-26 18:38:50 - Removing audio file: audio_files/2_-_Sheriff/20250819_112409_604_2_-_Sheriff.mp3
2025-08-26 18:38:50 - Removing metadata file: audio_files/2_-_Sheriff/20250819_112409_604_2_-_Sheriff_metadata.json
2025-08-26 18:38:50 - Cleanup completed: Removed 15 audio files and 15 metadata files
2025-08-26 18:38:50 - Total files removed: 30 (Before: 4269, After: 4239)
2025-08-26 18:38:50 - Cleanup process finished
```
