#!/bin/bash
#
# recorder.sh - Master control script for Police Radio Stream Recorder
# Provides unified access to all recording operations
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/scripts"

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

# Show usage
show_help() {
    cat << EOF
🎵 Police Radio Stream Recorder - Master Control Script

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    start [--background|--daemon]  Start recording (foreground or background)
    stop                          Stop recording
    status                        Show recording status
    web [--background|--daemon]   Start web UI (foreground or background)
    web-stop                      Stop web UI
    web-status                    Show web UI status
    dev                          Start development web server
    cleanup                       Clean up old recordings
    help                         Show this help message

EXAMPLES:
    $0 start                     # Start recording in foreground
    $0 start --background        # Start recording as daemon
    $0 stop                      # Stop recording
    $0 status                    # Check recording status
    $0 web --background          # Start web UI as daemon
    $0 web-stop                  # Stop web UI
    $0 web-status                # Check web UI status
    $0 dev                       # Start development web server
    $0 cleanup                   # Clean up old recordings

SCRIPT LOCATIONS:
    Main scripts:     $SCRIPTS_DIR/
    Development:      $SCRIPT_DIR/dev/
    Tests:           $SCRIPT_DIR/tests/
    
EOF
}

# Execute the appropriate script
case "$1" in
    "start")
        if [[ "$2" == "--background" || "$2" == "--daemon" ]]; then
            "$SCRIPTS_DIR/start_recording.sh" --background
        else
            "$SCRIPTS_DIR/start_recording.sh"
        fi
        ;;
    "stop")
        "$SCRIPTS_DIR/stop_recording.sh"
        ;;
    "status")
        "$SCRIPTS_DIR/start_recording.sh" --status
        ;;
    "web")
        if [[ "$2" == "--background" || "$2" == "--daemon" ]]; then
            "$SCRIPTS_DIR/start-web.sh" --background
        else
            "$SCRIPTS_DIR/start-web.sh"
        fi
        ;;
    "web-stop")
        "$SCRIPTS_DIR/start-web.sh" --stop
        ;;
    "web-status")
        "$SCRIPTS_DIR/start-web.sh" --status
        ;;
    "dev")
        "$SCRIPTS_DIR/start-dev.sh"
        ;;
    "cleanup")
        "$SCRIPTS_DIR/cleanup_old_recordings.sh"
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        print_color $RED "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
