#!/usr/bin/env python3
"""
Cleanup temporary audio files
"""

from audio_recorder import AudioRecorder

def main():
    print("Starting temp file cleanup...")
    
    # Create AudioRecorder instance
    recorder = AudioRecorder()
    
    # Clean up all temp files
    removed_count = recorder.cleanup_all_temp_files()
    
    print(f"Cleanup complete: removed {removed_count} temporary files")

if __name__ == '__main__':
    main()
