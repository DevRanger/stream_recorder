#!/usr/bin/env python3
"""
Quick start script to begin recording a few channels
"""
from audio_recorder import AudioRecorder
import time

def main():
    print("🎵 Starting recording for selected channels...")
    
    # Initialize audio recorder
    recorder = AudioRecorder()
    
    # Start recording for a few channels
    test_channels = ['2_-_Sheriff', '18_-_EPA', '20_-_Menlo_Park', '22_-_Redwood_City']
    
    for channel_id in test_channels:
        if channel_id in recorder.channels:
            recorder.start_recording([channel_id])
            print(f"✅ Started recording: {recorder.channels[channel_id]['name']}")
        else:
            print(f"❌ Channel not found: {channel_id}")
    
    print(f"\n📻 Recording {len(test_channels)} channels...")
    print("Recording will continue in background. Check the UI at http://localhost:5000")
    print("Files will be saved to audio_files/ directory")
    
    # Keep the script running
    try:
        while True:
            time.sleep(60)
            print(f"📊 Status: {len(recorder.is_recording)} channels recording")
    except KeyboardInterrupt:
        print("\n🛑 Stopping recording...")
        recorder.stop_recording()
        print("✅ Recording stopped")

if __name__ == '__main__':
    main()
