#!/usr/bin/env python3
"""
Test script for volume sensitivity tuning with the simplified RMS detection system
"""

import time
import os
from audio_recorder import AudioRecorder

def main():
    print("🔊 Volume Sensitivity Tuning Test")
    print("=" * 50)
    
    recorder = AudioRecorder()
    
    # Test channel
    test_channel = "25_-_San_Mateo"  # Known active channel
    
    if test_channel not in recorder.channels:
        print(f"❌ Channel {test_channel} not found!")
        print("Available channels:")
        for ch_id, ch_info in recorder.channels.items():
            print(f"  {ch_id}: {ch_info['name']}")
        return
    
    channel_info = recorder.channels[test_channel]
    current_sensitivity = channel_info.get('volume_sensitivity', 0.01)
    
    print(f"📻 Testing channel: {channel_info['name']}")
    print(f"🔊 Current volume sensitivity: {current_sensitivity}")
    print("🎯 This test will record for 60 seconds to evaluate current settings")
    print()
    
    print("💡 Volume sensitivity guide:")
    print("  0.001-0.005: Very sensitive (captures quiet audio)")
    print("  0.006-0.010: Medium sensitivity (balanced)")
    print("  0.011-0.020: Less sensitive (only louder audio)")
    print("  0.021+:      Low sensitivity (very loud audio only)")
    print()
    
    # Start recording
    print("🔴 Starting test recording...")
    recorder.start_recording([test_channel])
    
    # Record for 60 seconds
    print("⏱️  Recording for 60 seconds...")
    for i in range(12):
        time.sleep(5)
        print(f"   {(i + 1) * 5}/60 seconds", end="\r")
    
    print("\n🛑 Stopping recording...")
    recorder.stop_recording([test_channel])
    
    # Analyze results
    print("\n📋 Test Results:")
    channel_dir = os.path.join("audio_files", test_channel)
    
    if os.path.exists(channel_dir):
        import glob
        from datetime import datetime
        
        # Get recent FLAC files (last 5 minutes)
        now = datetime.now()
        recent_files = []
        
        flac_files = glob.glob(os.path.join(channel_dir, "*.flac"))
        for file in flac_files:
            if "temp_" not in file:
                file_time = os.path.getmtime(file)
                file_datetime = datetime.fromtimestamp(file_time)
                if (now - file_datetime).total_seconds() < 300:  # Last 5 minutes
                    recent_files.append(file)
        
        if recent_files:
            print(f"✅ {len(recent_files)} recordings captured:")
            total_size = 0
            for file in recent_files:
                size = os.path.getsize(file)
                total_size += size
                print(f"   📁 {os.path.basename(file)} ({size:,} bytes)")
            
            print(f"\n📊 Total: {total_size:,} bytes in {len(recent_files)} files")
            
            if len(recent_files) > 10:
                print("⚠️  Many files captured - consider INCREASING volume_sensitivity")
                print(f"   Try: {current_sensitivity * 1.5:.3f} or higher")
            elif len(recent_files) < 2:
                print("⚠️  Few files captured - consider DECREASING volume_sensitivity")
                print(f"   Try: {current_sensitivity * 0.7:.3f} or lower")
            else:
                print("✅ Good balance - current sensitivity seems appropriate")
        else:
            print("❌ No recordings captured!")
            print("💡 Consider DECREASING volume_sensitivity to capture more audio")
            print(f"   Try: {current_sensitivity * 0.5:.3f}")
    else:
        print("❌ No audio directory found")
    
    print("\n🔧 To adjust volume sensitivity:")
    print("1. Edit radio_channels.json")
    print(f"2. Find '{test_channel}' and change 'volume_sensitivity'")
    print("3. Restart recording and test again")

if __name__ == "__main__":
    main()
