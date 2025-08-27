#!/bin/bash
# Stop recording batch script for Police Radio Audio Logger

echo "🛑 Police Radio Audio Logger - Stop Recording"
echo "============================================="

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Run the Python stop script with uv
uv run python stop_recording.py

echo ""
echo "📝 To monitor the status, run the web UI with:"
echo "   uv run python main.py"
