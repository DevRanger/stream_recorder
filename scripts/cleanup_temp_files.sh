#!/bin/bash
#
# Cleanup temporary audio files script
# Usage: ./cleanup_temp_files.sh [force]
#
# Options:
#   force - Remove all temp files regardless of age

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🧹 Stream Recorder - Temp File Cleanup"
echo "======================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found at .venv"
    echo "   Please run setup first."
    exit 1
fi

# Activate virtual environment and run cleanup
echo "📁 Cleaning up temporary audio files..."

if [ "$1" = "force" ]; then
    echo "🔥 Force mode: Removing ALL temp files"
    .venv/bin/python -c "
from audio_recorder import AudioRecorder
recorder = AudioRecorder()
count = recorder.cleanup_temp_files(max_age_hours=0)
print(f'✅ Cleanup complete: Removed {count} temporary files')
"
else
    echo "⏰ Standard mode: Removing temp files older than 1 hour"
    .venv/bin/python cleanup_temp.py
fi

echo "✅ Temp file cleanup complete!"
