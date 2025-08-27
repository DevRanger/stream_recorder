#!/bin/bash

# cleanup_old_recordings.sh
# Script to remove audio recordings older than 7 days
# Designed to be run from crontab for automatic cleanup
#
# Usage: ./cleanup_old_recordings.sh
# Crontab example (run daily at 2 AM):
# 0 2 * * * /home/daryl/Python_Projects/stream_recorder/cleanup_old_recordings.sh

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIO_DIR="$SCRIPT_DIR/audio_files"
LOG_FILE="$SCRIPT_DIR/cleanup.log"
DAYS_OLD=7

# Function to log messages with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to count files before cleanup
count_files() {
    find "$AUDIO_DIR" -type f -name "*.mp3" -o -name "*.json" | wc -l
}

# Start cleanup process
log_message "Starting cleanup of audio files older than $DAYS_OLD days"

# Check if audio_files directory exists
if [ ! -d "$AUDIO_DIR" ]; then
    log_message "ERROR: Audio directory not found: $AUDIO_DIR"
    exit 1
fi

# Count files before cleanup
BEFORE_COUNT=$(count_files)
log_message "Total audio files before cleanup: $BEFORE_COUNT"

# Find and remove audio files (.mp3) older than 7 days
REMOVED_MP3=$(find "$AUDIO_DIR" -type f -name "*.mp3" -mtime +$DAYS_OLD -print)
if [ -n "$REMOVED_MP3" ]; then
    echo "$REMOVED_MP3" | while read -r file; do
        log_message "Removing audio file: $file"
        rm -f "$file"
    done
    MP3_COUNT=$(echo "$REMOVED_MP3" | wc -l)
else
    MP3_COUNT=0
fi

# Find and remove metadata files (.json) older than 7 days
REMOVED_JSON=$(find "$AUDIO_DIR" -type f -name "*_metadata.json" -mtime +$DAYS_OLD -print)
if [ -n "$REMOVED_JSON" ]; then
    echo "$REMOVED_JSON" | while read -r file; do
        log_message "Removing metadata file: $file"
        rm -f "$file"
    done
    JSON_COUNT=$(echo "$REMOVED_JSON" | wc -l)
else
    JSON_COUNT=0
fi

# Remove any empty directories
find "$AUDIO_DIR" -type d -empty -delete 2>/dev/null

# Count files after cleanup
AFTER_COUNT=$(count_files)
TOTAL_REMOVED=$((BEFORE_COUNT - AFTER_COUNT))

# Log summary
log_message "Cleanup completed: Removed $MP3_COUNT audio files and $JSON_COUNT metadata files"
log_message "Total files removed: $TOTAL_REMOVED (Before: $BEFORE_COUNT, After: $AFTER_COUNT)"
log_message "Cleanup process finished"
echo ""

# Exit successfully
exit 0
