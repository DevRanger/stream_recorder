#!/usr/bin/env python3
"""
Cleanup temporary audio files
"""

from audio_recorder import AudioRecorder

def main():
    print("Starting temp file cleanup...")
    
    # Create AudioRecorder instance
    recorder = AudioRecorder()
    
    # Clean up all temp files (force cleanup regardless of age)
    removed_count = recorder.cleanup_temp_files(max_age_hours=0)
    
    print(f"Cleanup complete: removed {removed_count} temporary files")

if __name__ == '__main__':
    main()
