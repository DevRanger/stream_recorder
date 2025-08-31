# Changelog

All notable changes to the Radio Stream Recorder project will be documented in this file.

## [1.1.0] - 2025-08-31

### Added
- **Modal Window Refresh Button**: Real-time refresh capability for recording lists without closing modal
- **Batch Download Feature**: Concatenate multiple selected recordings into single FLAC file
  - Automatic chronological sorting (oldest to newest)
  - Smart filename generation with timestamp ranges
  - Progress indicators and error handling
  - FFmpeg-based concatenation for efficient processing
- **Enhanced Modal Interface**: 
  - Improved header layout with grouped controls
  - Better visual feedback during operations
  - Responsive button states

### Changed
- **Audio Format**: Migrated from MP3 to FLAC for lossless audio quality
- **Production Compatibility**: Fixed hardcoded paths for deployment flexibility
  - Uses absolute paths based on script location
  - Works correctly regardless of working directory
  - Container and systemd service ready
- **Timestamp Display**: Fixed timezone issues
  - All timestamps now display in correct local time (PDT)
  - Proper JavaScript date parsing without UTC conversion
  - Consistent time display between filenames and UI

### Fixed
- **Path Resolution**: Resolved 404 errors in production deployments
- **Concatenation Endpoint**: Fixed FFmpeg file path issues for reliable audio processing
- **Modal Button Visibility**: Ensured batch control buttons display correctly
- **Memory Management**: Proper temporary file handling for concatenated downloads

### Technical Improvements
- Absolute path resolution using `__file__` directory
- Enhanced error logging for debugging concatenation issues
- Improved Flask response handling for file downloads
- Better separation of development and production path handling

## [1.0.0] - 2025-08-29

### Initial Release
- Multi-channel radio recording system
- Web interface for monitoring and playback
- Voice activity detection
- Automatic file cleanup
- Batch playback functionality
- RESTful API for external integration
