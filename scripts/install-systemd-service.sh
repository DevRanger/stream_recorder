#!/bin/bash
#
# install-systemd-service.sh - Install Stream Recorder Web UI as systemd service
# Works with any deployment path (auto-detects project location)
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_NAME="stream-recorder-web"
SERVICE_TEMPLATE="$PROJECT_ROOT/${SERVICE_NAME}.service.template"
SERVICE_FILE="/tmp/${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

# Auto-detect current user and group
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    echo -e "${1}${2}${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_color $RED "❌ Do not run this script as root!"
        print_color $YELLOW "💡 Run as your regular user. sudo will be used when needed."
        exit 1
    fi
}

# Check if service template exists
check_service_template() {
    if [[ ! -f "$SERVICE_TEMPLATE" ]]; then
        print_color $RED "❌ Service template not found: $SERVICE_TEMPLATE"
        exit 1
    fi
}

# Generate service file from template
generate_service_file() {
    print_color $BLUE "🔧 Generating systemd service file..."
    print_color $BLUE "📁 Project Root: $PROJECT_ROOT"
    print_color $BLUE "👤 User: $CURRENT_USER"
    print_color $BLUE "👥 Group: $CURRENT_GROUP"
    
    # Replace placeholders in template
    sed -e "s|__PROJECT_ROOT__|$PROJECT_ROOT|g" \
        -e "s|__USER__|$CURRENT_USER|g" \
        -e "s|__GROUP__|$CURRENT_GROUP|g" \
        "$SERVICE_TEMPLATE" > "$SERVICE_FILE"
    
    if [[ ! -f "$SERVICE_FILE" ]]; then
        print_color $RED "❌ Failed to generate service file"
        exit 1
    fi
    
    print_color $GREEN "✅ Service file generated: $SERVICE_FILE"
}

# Install the service
install_service() {
    print_color $BLUE "🔧 Installing Stream Recorder Web UI systemd service..."
    
    # Copy service file
    sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/"
    
    # Set proper permissions
    sudo chmod 644 "$SYSTEMD_DIR/${SERVICE_NAME}.service"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Clean up temporary file
    rm -f "$SERVICE_FILE"
    
    print_color $GREEN "✅ Service installed successfully"
}

# Show usage instructions
show_usage() {
    cat << EOF

🎉 Stream Recorder Web UI Service Installation Complete!

SYSTEMD COMMANDS:
    sudo systemctl start ${SERVICE_NAME}      # Start the service
    sudo systemctl stop ${SERVICE_NAME}       # Stop the service
    sudo systemctl restart ${SERVICE_NAME}    # Restart the service
    sudo systemctl status ${SERVICE_NAME}     # Check service status
    sudo systemctl enable ${SERVICE_NAME}     # Enable auto-start on boot
    sudo systemctl disable ${SERVICE_NAME}    # Disable auto-start on boot

LOGS:
    sudo journalctl -u ${SERVICE_NAME}        # View service logs
    sudo journalctl -u ${SERVICE_NAME} -f    # Follow service logs
    tail -f $PROJECT_ROOT/logs/gunicorn_error.log  # Gunicorn error logs
    tail -f $PROJECT_ROOT/logs/gunicorn_access.log # Gunicorn access logs

MANUAL CONTROL (alternative to systemd):
    $PROJECT_ROOT/scripts/start-web.sh --background  # Start manually
    $PROJECT_ROOT/scripts/start-web.sh --stop        # Stop manually
    $PROJECT_ROOT/scripts/start-web.sh --status      # Check status

WEB ACCESS:
    http://localhost:8000

CONFIGURATION:
    Project Root: $PROJECT_ROOT
    User/Group:   $CURRENT_USER:$CURRENT_GROUP
    Service Name: $SERVICE_NAME

NEXT STEPS:
    1. Enable auto-start: sudo systemctl enable ${SERVICE_NAME}
    2. Start the service: sudo systemctl start ${SERVICE_NAME}
    3. Check status: sudo systemctl status ${SERVICE_NAME}
    4. Access web UI: http://localhost:8000

EOF
}

# Main installation process
main() {
    print_color $BLUE "🚀 Stream Recorder Web UI - Systemd Service Installer"
    print_color $BLUE "======================================================"
    
    check_root
    check_service_template
    generate_service_file
    install_service
    show_usage
}

# Run installation
main "$@"
