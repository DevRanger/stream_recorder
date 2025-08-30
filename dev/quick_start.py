#!/usr/bin/env python3
"""
Quick start script to begin recording channels with simplified RMS detection
"""
from audio_recorder import AudioRecorder
import time

def main():
    print("🎵 Starting recording for selected channels with RMS-based detection...")
    
    # Initialize audio recorder
    recorder = AudioRecorder()
    
    # Start recording for a few channels with known good settings
    test_channels = ['2_-_Sheriff', '18_-_EPA', '20_-_Menlo_Park', '22_-_Redwood_City']
    
    print("📊 Channel volume sensitivity settings:")
    for channel_id in test_channels:
        if channel_id in recorder.channels:
            volume_sensitivity = recorder.channels[channel_id].get('volume_sensitivity', 0.01)
            print(f"  {recorder.channels[channel_id]['name']}: {volume_sensitivity}")
    
    print("\n🔴 Starting recording...")
    for channel_id in test_channels:
        if channel_id in recorder.channels:
            recorder.start_recording([channel_id])
            print(f"✅ Started recording: {recorder.channels[channel_id]['name']}")
        else:
            print(f"❌ Channel not found: {channel_id}")
    
    print(f"\n📻 Recording {len(test_channels)} channels with simplified detection...")
    print("🎯 Only audio with RMS > volume_sensitivity will be saved as FLAC files")
    print("🌐 Check the UI at http://localhost:8000")
    print("📁 Files will be saved to audio_files/ directory")
    
    # Keep the script running
    try:
        while True:
            time.sleep(60)
            active_count = sum(1 for v in recorder.is_recording.values() if v)
            print(f"📊 Status: {active_count} channels actively recording")
    except KeyboardInterrupt:
        print("\n🛑 Stopping recording...")
        recorder.stop_recording()
        print("✅ Recording stopped")

if __name__ == '__main__':
    main()
