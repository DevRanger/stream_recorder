#!/bin/bash
# Start recording batch script for Police Radio Audio Logger

echo "🎵 Police Radio Audio Logger - Start Recording"
echo "=============================================="

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Check if user wants to run in background
if [[ "$1" == "--background" || "$1" == "-bg" ]]; then
    echo "🔄 Starting recording in background..."
    nohup uv run python scripts/start_recording.py > recording.log 2>&1 &
    echo "✅ Recording started in background (PID: $!)"
    echo "📄 Log file: recording.log"
    echo "🛑 To stop recording, run: ./scripts/stop_recording.sh"
else
    echo "🔄 Starting recording (will run in foreground)..."
    echo "💡 Tip: Use './scripts/start_recording.sh --background' to run in background"
    echo ""
    
    # Run the Python start script with uv
    uv run python scripts/start_recording.py
fi

echo ""
echo "📝 To monitor the recording status, run the web UI with:"
echo "   uv run python main.py"
echo ""
echo "🛑 To stop recording, run:"
echo "   ./stop_recording.sh"
