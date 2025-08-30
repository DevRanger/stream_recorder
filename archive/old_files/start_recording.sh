#!/bin/bash
#
# start_recording.sh - Police Radio Stream Recorder Control Script
# Usage: ./start_recording.sh [--background|--daemon] [--stop] [--status] [--help]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/start_recording.py"
PID_FILE="$SCRIPT_DIR/recording.pid"
LOG_FILE="$SCRIPT_DIR/recording.log"
PYTHON_EXEC="$SCRIPT_DIR/.venv/bin/python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_color() {
    echo -e "${1}${2}${NC}"
}

# Check if Python virtual environment exists
check_python() {
    if [[ ! -f "$PYTHON_EXEC" ]]; then
        print_color $RED "❌ Python virtual environment not found at $PYTHON_EXEC"
        print_color $YELLOW "💡 Run: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
        exit 1
    fi
}

# Check if the recorder is running
is_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            # PID file exists but process is dead, clean up
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Start recording in foreground
start_foreground() {
    if is_running; then
        print_color $YELLOW "⚠️  Recording is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_color $BLUE "🎵 Starting Police Radio Stream Recorder (foreground)..."
    check_python
    exec "$PYTHON_EXEC" "$PYTHON_SCRIPT"
}

# Start recording in background/daemon mode
start_background() {
    if is_running; then
        print_color $YELLOW "⚠️  Recording is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_color $BLUE "🎵 Starting Police Radio Stream Recorder (daemon mode)..."
    check_python
    
    # Start the Python script in background and capture PID
    nohup "$PYTHON_EXEC" "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # Save PID to file
    echo "$pid" > "$PID_FILE"
    
    # Give it a moment to start
    sleep 2
    
    # Verify it's actually running
    if is_running; then
        print_color $GREEN "✅ Recording started successfully in background"
        print_color $BLUE "📄 PID: $(cat "$PID_FILE")"
        print_color $BLUE "📄 Logs: $LOG_FILE"
        print_color $BLUE "🛑 Stop with: $0 --stop"
    else
        print_color $RED "❌ Failed to start recording in background"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop recording
stop_recording() {
    if ! is_running; then
        print_color $YELLOW "⚠️  Recording is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_color $BLUE "🛑 Stopping recording (PID: $pid)..."
    
    # Send SIGTERM first for graceful shutdown
    kill -TERM "$pid" 2>/dev/null
    
    # Wait up to 10 seconds for graceful shutdown
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        ((count++))
    done
    
    # If still running, force kill
    if ps -p "$pid" > /dev/null 2>&1; then
        print_color $YELLOW "⚠️  Graceful shutdown failed, forcing stop..."
        kill -KILL "$pid" 2>/dev/null
        sleep 1
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
    
    if ! ps -p "$pid" > /dev/null 2>&1; then
        print_color $GREEN "✅ Recording stopped successfully"
    else
        print_color $RED "❌ Failed to stop recording"
        return 1
    fi
}

# Show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_color $GREEN "✅ Recording is RUNNING"
        print_color $BLUE "📄 PID: $pid"
        print_color $BLUE "📄 Log file: $LOG_FILE"
        
        # Show recent log entries
        if [[ -f "$LOG_FILE" ]]; then
            print_color $BLUE "📄 Recent log entries:"
            tail -5 "$LOG_FILE" | while IFS= read -r line; do
                echo "   $line"
            done
        fi
    else
        print_color $YELLOW "🔇 Recording is NOT running"
    fi
}

# Show usage
show_help() {
    cat << EOF
Police Radio Stream Recorder Control Script

Usage: $0 [OPTION]

OPTIONS:
    --background, --daemon    Start recording in background/daemon mode
    --stop                   Stop recording
    --status                 Show recording status
    --help                   Show this help message
    
    (no options)             Start recording in foreground mode

EXAMPLES:
    $0                       # Start in foreground
    $0 --background          # Start as daemon
    $0 --daemon              # Start as daemon (alias)
    $0 --stop                # Stop recording
    $0 --status              # Check status

FILES:
    $PID_FILE    - Process ID file
    $LOG_FILE     - Log output file
    $PYTHON_SCRIPT - Main Python script

EOF
}

# Main script logic
case "${1:-}" in
    --background|--daemon)
        start_background
        ;;
    --stop)
        stop_recording
        ;;
    --status)
        show_status
        ;;
    --help|-h)
        show_help
        ;;
    "")
        start_foreground
        ;;
    *)
        print_color $RED "❌ Unknown option: $1"
        print_color $YELLOW "💡 Use --help for usage information"
        exit 1
        ;;
esac
