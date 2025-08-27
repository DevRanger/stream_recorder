#!/bin/bash
#
# start-web.sh - Stream Recorder Web UI Control Script
# Usage: ./start-web.sh [--background|--daemon] [--stop] [--status] [--help]
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GUNICORN_CONF="$PROJECT_ROOT/gunicorn.conf.py"
PID_FILE="$PROJECT_ROOT/logs/gunicorn.pid"
LOG_DIR="$PROJECT_ROOT/logs"
WSGI_MODULE="main:app"

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

# Check if logs directory exists
check_logs_dir() {
    if [[ ! -d "$LOG_DIR" ]]; then
        mkdir -p "$LOG_DIR"
        print_color $YELLOW "📁 Created logs directory: $LOG_DIR"
    fi
}

# Check if the web UI is running
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

# Start web UI in foreground
start_foreground() {
    if is_running; then
        print_color $YELLOW "⚠️  Web UI is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_color $BLUE "🌐 Starting Stream Recorder Web UI (foreground)..."
    check_logs_dir
    
    cd "$PROJECT_ROOT"
    exec uv run gunicorn --config "$GUNICORN_CONF" "$WSGI_MODULE"
}

# Start web UI in background/daemon mode
start_background() {
    if is_running; then
        print_color $YELLOW "⚠️  Web UI is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    print_color $BLUE "🌐 Starting Stream Recorder Web UI (daemon mode)..."
    check_logs_dir
    
    cd "$PROJECT_ROOT"
    
    # Start Gunicorn in background
    nohup uv run gunicorn --config "$GUNICORN_CONF" "$WSGI_MODULE" > /dev/null 2>&1 &
    local pid=$!
    
    # Give it a moment to start
    sleep 3
    
    # Verify it's actually running
    if is_running; then
        print_color $GREEN "✅ Web UI started successfully in background"
        print_color $BLUE "📄 PID: $(cat "$PID_FILE")"
        print_color $BLUE "📄 Access: http://localhost:8000"
        print_color $BLUE "📄 Logs: $LOG_DIR/"
        print_color $BLUE "🛑 Stop with: $0 --stop"
    else
        print_color $RED "❌ Failed to start Web UI in background"
        return 1
    fi
}

# Stop web UI
stop_web() {
    if ! is_running; then
        print_color $YELLOW "⚠️  Web UI is not running"
        return 1
    fi
    
    local pid=$(cat "$PID_FILE")
    print_color $BLUE "🛑 Stopping Web UI (PID: $pid)..."
    
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
        print_color $GREEN "✅ Web UI stopped successfully"
    else
        print_color $RED "❌ Failed to stop Web UI"
        return 1
    fi
}

# Show status
show_status() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        print_color $GREEN "✅ Web UI is RUNNING"
        print_color $BLUE "📄 PID: $pid"
        print_color $BLUE "📄 URL: http://localhost:8000"
        print_color $BLUE "📄 Config: $GUNICORN_CONF"
        print_color $BLUE "📄 Logs: $LOG_DIR/"
        
        # Show recent log entries
        if [[ -f "$LOG_DIR/gunicorn_error.log" ]]; then
            print_color $BLUE "📄 Recent error log entries:"
            tail -3 "$LOG_DIR/gunicorn_error.log" | while IFS= read -r line; do
                echo "   $line"
            done
        fi
    else
        print_color $YELLOW "🔇 Web UI is NOT running"
    fi
}

# Show usage
show_help() {
    cat << EOF
Stream Recorder Web UI Control Script

Usage: $0 [OPTION]

OPTIONS:
    --background, --daemon    Start Web UI in background/daemon mode
    --stop                   Stop Web UI
    --status                 Show Web UI status
    --help                   Show this help message
    
    (no options)             Start Web UI in foreground mode

EXAMPLES:
    $0                       # Start in foreground
    $0 --background          # Start as daemon
    $0 --daemon              # Start as daemon (alias)
    $0 --stop                # Stop Web UI
    $0 --status              # Check status

CONFIGURATION:
    Config file: $GUNICORN_CONF
    PID file:    $PID_FILE
    Logs:        $LOG_DIR/
    URL:         http://localhost:8000

EOF
}

# Main script logic
case "$1" in
    "--background"|"--daemon")
        start_background
        ;;
    "--stop")
        stop_web
        ;;
    "--status")
        show_status
        ;;
    "--help"|"-h")
        show_help
        ;;
    "")
        start_foreground
        ;;
    *)
        print_color $RED "❌ Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
