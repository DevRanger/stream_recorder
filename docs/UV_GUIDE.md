# UV Quick Reference

## Overview

This project uses [UV](https://docs.astral.sh/uv/) for Python package management. UV is a fast Python package installer and resolver, written in Rust, that provides a modern alternative to pip and virtual environments.

## Basic Commands

### Project Setup
```bash
# Install dependencies (creates .venv automatically)
uv sync

# Install in development mode with all optional dependencies
uv sync --all-extras
```

### Running Code
```bash
# Run Python scripts with project dependencies
uv run python main.py
uv run python start_recording.py

# Run with environment variables
FLASK_ENV=development uv run python main.py

# Run scripts from scripts directory
./scripts/start-dev.sh
./scripts/start_recording.sh
./scripts/stop_recording.sh
```

### Package Management
```bash
# Add a new dependency
uv add flask

# Add a development dependency
uv add --dev pytest

# Add a dependency with version constraints
uv add "requests>=2.25.0"

# Remove a dependency
uv remove package-name

# Update all dependencies
uv sync --upgrade

# Show installed packages
uv pip list
```

### Virtual Environment
```bash
# UV automatically manages .venv, but you can also:
# Activate the virtual environment manually
source .venv/bin/activate

# Deactivate (when manually activated)
deactivate

# Remove the virtual environment
rm -rf .venv
uv sync  # Recreates it
```

## Project-Specific Usage

### Starting the Application
```bash
# Development server
uv run python main.py

# Or use the startup script
./scripts/start-dev.sh

# Background recording
./scripts/start_recording.sh --background
```

### Running Tests
```bash
# Run unit tests
uv run python -m pytest tests/

# Run specific test files
uv run python dev/test_api.py
uv run python dev/test_timestamp.py
```

### Development Utilities
```bash
# Channel health monitoring
uv run python dev/channel_health_monitor.py

# Manual temp file cleanup
uv run python dev/cleanup_temp.py

# Quick development setup
uv run python dev/quick_start.py
```

### Maintenance Tasks
```bash
# Manual cleanup (using Python script)
uv run python -c "
from audio_recorder import AudioRecorder
recorder = AudioRecorder()
recorder.cleanup_temp_files()
"

# Check application imports
uv run python -c "import main; print('✓ Application ready')"
```

## Configuration Files

### `pyproject.toml`
The main project configuration file that defines:
- Project metadata
- Dependencies
- Build configuration
- Tool settings

### `uv.lock`
Lock file that pins exact versions of all dependencies for reproducible builds. This file should be committed to version control.

### `.python-version`
Specifies the Python version to use. UV will respect this when creating virtual environments.

## Troubleshooting

### Common Issues

**Dependencies not found:**
```bash
uv sync  # Reinstall dependencies
```

**Python version issues:**
```bash
# Install specific Python version
uv python install 3.11

# Use specific Python version
uv python pin 3.11
```

**Virtual environment issues:**
```bash
# Remove and recreate environment
rm -rf .venv
uv sync
```

**Permission errors:**
```bash
# Make sure scripts are executable
chmod +x scripts/*.sh
```

### Performance Tips

**Fast dependency installation:**
UV is already very fast, but you can:
- Use `uv sync --frozen` to skip dependency resolution
- Use `uv cache clean` to clear package cache if needed

**Development workflow:**
```bash
# For rapid development iterations
uv run python main.py

# For testing changes
uv run python -c "import your_module; your_module.test_function()"
```

## Integration with Project Tools

### With Shell Scripts
All shell scripts in `scripts/` use `uv run` for Python execution:
```bash
# scripts/start-dev.sh
uv run python main.py

# scripts/start_recording.sh
uv run python start_recording.py
```

### With Cron Jobs
For scheduled tasks, use absolute paths:
```bash
# In crontab
0 2 * * * cd /path/to/stream_recorder && /usr/local/bin/uv run python scripts/cleanup_old_recordings.py
```

### With Systemd Services
For production deployment:
```ini
[Unit]
Description=Stream Recorder

[Service]
Type=simple
User=radio
WorkingDirectory=/opt/stream_recorder
ExecStart=/usr/local/bin/uv run python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Migration from Other Tools

### From pip + virtualenv
If you were using pip and virtualenv:
1. Remove old virtual environment: `rm -rf venv/`
2. Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Initialize with UV: `uv sync`
4. Update scripts to use `uv run` instead of direct Python calls

### From Poetry
If migrating from Poetry:
1. UV can read Poetry's `pyproject.toml` files
2. Run `uv sync` to install dependencies
3. Update CI/CD pipelines to use UV commands

### From Conda
If migrating from Conda:
1. Export requirements: `conda list --export > requirements.txt`
2. Convert to UV format in `pyproject.toml`
3. Use `uv sync` for dependency management

## Best Practices

### Development
- Always use `uv run` for running Python scripts
- Commit `uv.lock` for reproducible builds
- Use `uv add --dev` for development-only dependencies
- Regularly update dependencies with `uv sync --upgrade`

### Production
- Use `uv sync --frozen` for deployment
- Pin exact versions in `pyproject.toml` for critical dependencies
- Use `uv pip compile` for generating requirements.txt if needed

### Collaboration
- Commit both `pyproject.toml` and `uv.lock`
- Document any system dependencies (like ffmpeg)
- Use consistent Python versions across environments

## Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [UV GitHub Repository](https://github.com/astral-sh/uv)
- [Project's pyproject.toml](./pyproject.toml)
- [Installation Guide](./INSTALLATION.md)
