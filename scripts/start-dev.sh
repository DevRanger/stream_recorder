#!/bin/bash
# Development server start script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Stream Recorder Flask App..."
echo "📦 Using UV package manager"
echo "📁 Project Root: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Set development environment
export FLASK_ENV=development
export PORT=8000

# Start the server
uv run python main.py
