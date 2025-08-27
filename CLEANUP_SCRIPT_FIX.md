# Cleanup Script Path Fix

## Problem
The `cleanup_old_recordings.sh` script was using incorrect relative paths. It was looking for the `audio_files` directory inside the `scripts/` directory instead of at the project root level.

## Changes Made

### 1. Fixed Path Resolution
**Before:**
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIO_DIR="$SCRIPT_DIR/audio_files"
LOG_FILE="$SCRIPT_DIR/cleanup.log"
```

**After:**
```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AUDIO_DIR="$PROJECT_ROOT/audio_files"
LOG_FILE="$PROJECT_ROOT/cleanup.log"
```

### 2. Updated Crontab Example
**Before:**
```bash
# 0 2 * * * /home/daryl/Python_Projects/stream_recorder/cleanup_old_recordings.sh
```

**After:**
```bash
# 0 2 * * * /home/daryl/Python_Projects/stream_recorder/scripts/cleanup_old_recordings.sh
```

### 3. Updated Documentation
- Enhanced script README with more detailed description
- Updated main README with correct paths and alternative using master control script

## Directory Structure
```
stream_recorder/                    # PROJECT_ROOT
├── audio_files/                   # Target directory for cleanup
├── cleanup.log                    # Log file location
├── scripts/
│   └── cleanup_old_recordings.sh  # Script location
└── recorder.sh                    # Master control script
```

## Path Resolution Logic
1. **SCRIPT_DIR**: `/home/daryl/Python_Projects/stream_recorder/scripts`
2. **PROJECT_ROOT**: `/home/daryl/Python_Projects/stream_recorder` (SCRIPT_DIR/..)
3. **AUDIO_DIR**: `/home/daryl/Python_Projects/stream_recorder/audio_files`
4. **LOG_FILE**: `/home/daryl/Python_Projects/stream_recorder/cleanup.log`

## Verification
✅ Script runs correctly from any location
✅ Finds audio_files directory at project root
✅ Creates log file in project root
✅ Works through master control script (`./recorder.sh cleanup`)
✅ Crontab examples use correct paths

## Usage Options
```bash
# Direct execution
./scripts/cleanup_old_recordings.sh

# Via master control script
./recorder.sh cleanup

# Crontab (daily at 2 AM)
0 2 * * * /home/daryl/Python_Projects/stream_recorder/scripts/cleanup_old_recordings.sh

# Alternative crontab using master script
0 2 * * * /home/daryl/Python_Projects/stream_recorder/recorder.sh cleanup
```
