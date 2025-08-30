#!/bin/bash

# Cleanup script for removing short FLAC files with no meaningful audio
# This script removes FLAC files shorter than 2.0 seconds (2000ms)

AUDIO_DIR="audio_files"
MIN_DURATION_MS=2000  # 2.0 seconds minimum (updated from 1.5s)
LOG_FILE="cleanup_short_files.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to get duration from metadata file
get_duration_from_metadata() {
    local audio_file="$1"
    local metadata_file="${audio_file%.*}_metadata.json"
    
    if [ -f "$metadata_file" ]; then
        # Extract duration_ms from JSON file
        duration=$(grep -o '"duration_ms": [0-9]*' "$metadata_file" | grep -o '[0-9]*')
        echo "$duration"
    else
        echo "0"  # No metadata, assume it should be removed
    fi
}

# Function to count short files before cleanup
count_short_files() {
    local count=0
    for flac_file in $(find "$AUDIO_DIR" -name "*.flac" -type f); do
        duration=$(get_duration_from_metadata "$flac_file")
        if [ "$duration" -lt "$MIN_DURATION_MS" ] && [ "$duration" -gt 0 ]; then
            count=$((count + 1))
        fi
    done
    echo "$count"
}

# Start cleanup process
log_message "Starting cleanup of short FLAC files (< ${MIN_DURATION_MS}ms)"

# Check if audio_files directory exists
if [ ! -d "$AUDIO_DIR" ]; then
    log_message "ERROR: Audio directory not found: $AUDIO_DIR"
    exit 1
fi

# Count short files before cleanup
BEFORE_COUNT=$(count_short_files)
log_message "Found $BEFORE_COUNT short FLAC files to remove"

if [ "$BEFORE_COUNT" -eq 0 ]; then
    log_message "No short files found. Cleanup not needed."
    exit 0
fi

# Remove short FLAC files and their metadata
removed_count=0
removed_metadata_count=0

for flac_file in $(find "$AUDIO_DIR" -name "*.flac" -type f); do
    duration=$(get_duration_from_metadata "$flac_file")
    
    if [ "$duration" -lt "$MIN_DURATION_MS" ]; then
        # Remove the FLAC file
        log_message "Removing short file: $flac_file (${duration}ms)"
        rm -f "$flac_file"
        removed_count=$((removed_count + 1))
        
        # Remove corresponding metadata file if it exists
        metadata_file="${flac_file%.*}_metadata.json"
        if [ -f "$metadata_file" ]; then
            log_message "Removing metadata: $metadata_file"
            rm -f "$metadata_file"
            removed_metadata_count=$((removed_metadata_count + 1))
        fi
    fi
done

# Count short files after cleanup
AFTER_COUNT=$(count_short_files)

# Log summary
log_message "Cleanup completed:"
log_message "  - Removed $removed_count short FLAC files"
log_message "  - Removed $removed_metadata_count metadata files" 
log_message "  - Short files remaining: $AFTER_COUNT"
log_message "Cleanup process finished"

echo ""
echo "Summary:"
echo "  Short FLAC files removed: $removed_count"
echo "  Metadata files removed: $removed_metadata_count"
echo "  Check $LOG_FILE for detailed log"

exit 0
