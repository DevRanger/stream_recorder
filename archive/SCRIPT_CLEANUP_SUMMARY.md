# Script Directory Cleanup Summary

## Duplicate Files Removed

The following duplicate files have been moved from the project root to `archive/old_files/`:

### ✅ **Moved to Archive:**
- **`start_recording.py`** - Root version (basic, 67 lines) → Archived
- **`start_recording.sh`** - Root version (complex, 205 lines) → Archived  
- **`stop_recording.py`** - Root version (basic, 95 lines) → Archived

### 🗑️ **Deleted Duplicates:**
- **`dev/cleanup_temp.py`** - Identical duplicate of root `cleanup_temp.py` → Deleted

## Scripts Directory is Now Canonical

The `scripts/` directory now contains the **only and best versions** of these utilities:

### 🎯 **Canonical Script Locations:**
- **`scripts/start_recording.py`** - Robust version with path handling (77 lines)
- **`scripts/start_recording.sh`** - Clean, modern script using `uv run` (32 lines)
- **`scripts/stop_recording.py`** - Robust version with path handling (104 lines)
- **`scripts/stop_recording.sh`** - Simple, clean stop script (16 lines)

## Documentation Updated

### ✅ **Files Updated:**
- **`QUICK_START.md`** - Updated to reference `./scripts/start_recording.sh`
- **`QUICK_START.md`** - Updated web UI port from 5000 to 8000
- **`QUICK_START.md`** - Updated to use `uv run` commands

### ✅ **Already Correct:**
- **`README.md`** - Already references `scripts/` directory correctly
- **`scripts/README.md`** - Comprehensive documentation of script usage

## Benefits of Cleanup

### 🎯 **Eliminated Confusion:**
- No more duplicate files with different functionality
- Clear single source of truth for all utilities
- Consistent modern approach using `uv run`

### 🧹 **Simplified Structure:**
- Scripts organized in dedicated directory
- Clean project root
- Better separation of concerns

### 📚 **Better Documentation:**
- All references now point to correct locations
- Updated to reflect current system (port 8000, uv commands)
- Consistent usage examples

## Current Script Usage

### **Start Recording:**
```bash
./scripts/start_recording.sh                # Foreground
./scripts/start_recording.sh --background   # Background
```

### **Stop Recording:**
```bash
./scripts/stop_recording.sh
```

### **Web Interface:**
```bash
uv run python main.py                       # http://localhost:8000
```

### **Cleanup:**
```bash
uv run python cleanup_temp.py               # Clean temp files
```

## Script Directory Contents

The `scripts/` directory now contains:
- Core recording scripts (start/stop)
- System management scripts (cleanup, monitoring)
- Deployment scripts (production, systemd)
- Development scripts (start-dev, start-web)

All scripts are modern, use `uv run`, and handle project paths correctly.

*Cleanup completed: August 29, 2025*
