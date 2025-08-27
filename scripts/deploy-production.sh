#!/bin/bash
#
# deploy-production.sh - Deploy Stream Recorder to production location
# Usage: ./deploy-production.sh [TARGET_DIR]
#

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TARGET="/opt/stream_recorder"
TARGET_DIR="${1:-$DEFAULT_TARGET}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_color() {
    echo -e "${1}${2}${NC}"
}

# Check if running as root for system-wide deployment
check_permissions() {
    if [[ "$TARGET_DIR" == "/opt/"* ]] && [[ $EUID -ne 0 ]]; then
        print_color $RED "❌ Root privileges required for system-wide deployment to $TARGET_DIR"
        print_color $YELLOW "💡 Run with sudo or choose a user directory"
        exit 1
    fi
}

# Create target directory and copy files
deploy_files() {
    print_color $BLUE "📦 Deploying Stream Recorder to $TARGET_DIR"
    
    # Create target directory
    mkdir -p "$TARGET_DIR"
    
    # Copy all files except development-specific ones
    print_color $BLUE "📂 Copying application files..."
    
    # Core application files
    cp "$SOURCE_DIR"/*.py "$TARGET_DIR/" 2>/dev/null || true
    cp "$SOURCE_DIR"/*.json "$TARGET_DIR/" 2>/dev/null || true
    cp "$SOURCE_DIR"/*.sh "$TARGET_DIR/" 2>/dev/null || true
    cp "$SOURCE_DIR"/*.conf.py "$TARGET_DIR/" 2>/dev/null || true
    cp "$SOURCE_DIR"/*.service.template "$TARGET_DIR/" 2>/dev/null || true
    
    # Copy directories
    if [[ -d "$SOURCE_DIR/scripts" ]]; then
        cp -r "$SOURCE_DIR/scripts" "$TARGET_DIR/"
    fi
    
    if [[ -d "$SOURCE_DIR/templates" ]]; then
        cp -r "$SOURCE_DIR/templates" "$TARGET_DIR/"
    fi
    
    if [[ -d "$SOURCE_DIR/static" ]]; then
        cp -r "$SOURCE_DIR/static" "$TARGET_DIR/"
    fi
    
    if [[ -d "$SOURCE_DIR/docs" ]]; then
        cp -r "$SOURCE_DIR/docs" "$TARGET_DIR/"
    fi
    
    # Create necessary directories
    mkdir -p "$TARGET_DIR/logs"
    mkdir -p "$TARGET_DIR/audio_files"
    
    # Set proper permissions
    chmod +x "$TARGET_DIR"/*.sh
    chmod +x "$TARGET_DIR"/scripts/*.sh
    
    print_color $GREEN "✅ Files deployed successfully"
}

# Setup Python environment
setup_python_env() {
    print_color $BLUE "🐍 Setting up Python environment..."
    
    cd "$TARGET_DIR"
    
    # Check if uv is available
    if command -v uv &> /dev/null; then
        uv venv
        uv sync
    elif command -v python3 &> /dev/null; then
        python3 -m venv .venv
        .venv/bin/pip install -r pyproject.toml 2>/dev/null || print_color $YELLOW "⚠️  Could not install from pyproject.toml, install dependencies manually"
    else
        print_color $RED "❌ Python 3 not found. Please install Python 3 and dependencies manually"
        return 1
    fi
    
    print_color $GREEN "✅ Python environment setup complete"
}

# Set ownership for system deployment
set_ownership() {
    if [[ "$TARGET_DIR" == "/opt/"* ]] && [[ $EUID -eq 0 ]]; then
        print_color $BLUE "👤 Setting up user ownership..."
        
        # Create service user if deploying to /opt
        if ! id "stream-recorder" &>/dev/null; then
            useradd -r -s /bin/false -d "$TARGET_DIR" stream-recorder
            print_color $GREEN "✅ Created service user: stream-recorder"
        fi
        
        chown -R stream-recorder:stream-recorder "$TARGET_DIR"
        print_color $GREEN "✅ Ownership set to stream-recorder:stream-recorder"
    fi
}

# Show post-deployment instructions
show_instructions() {
    cat << EOF

🎉 Stream Recorder Deployment Complete!

DEPLOYMENT LOCATION: $TARGET_DIR

NEXT STEPS:

1. CONFIGURE ENVIRONMENT:
   cd $TARGET_DIR
   
2. TEST THE APPLICATION:
   # Start recording (background)
   ./recorder.sh start --background
   
   # Start web UI (background)  
   ./recorder.sh web --background
   
   # Check status
   ./recorder.sh status
   ./recorder.sh web-status

3. INSTALL SYSTEMD SERVICE (optional):
   cd $TARGET_DIR
   ./scripts/install-systemd-service.sh

4. SETUP AUTOMATED CLEANUP:
   # Add to crontab (adjust path as needed):
   0 2 * * * $TARGET_DIR/scripts/cleanup_old_recordings.sh

5. ACCESS WEB INTERFACE:
   http://localhost:8000

CONFIGURATION FILES:
   - Radio channels: $TARGET_DIR/radio_channels.json
   - Gunicorn config: $TARGET_DIR/gunicorn.conf.py

LOG LOCATIONS:
   - Application: $TARGET_DIR/recording.log
   - Web UI: $TARGET_DIR/logs/
   - Cleanup: $TARGET_DIR/cleanup.log

EOF

    if [[ "$TARGET_DIR" == "/opt/"* ]]; then
        cat << EOF
SYSTEMD SERVICE:
   sudo systemctl enable stream-recorder-web
   sudo systemctl start stream-recorder-web
   sudo systemctl status stream-recorder-web

EOF
    fi
}

# Main deployment process
main() {
    print_color $BLUE "🚀 Stream Recorder Production Deployment"
    print_color $BLUE "========================================"
    print_color $BLUE "Source: $SOURCE_DIR"
    print_color $BLUE "Target: $TARGET_DIR"
    echo ""
    
    check_permissions
    deploy_files
    setup_python_env
    set_ownership
    show_instructions
}

# Run deployment
main "$@"
