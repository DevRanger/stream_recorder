#!/usr/bin/env python3
"""
Voice Detection Test Script
Tests enhanced voice detection and stream reliability
"""

import time
import os
from audio_recorder import AudioRecorder


def main():
    print("🎙️ Testing Enhanced Voice Detection and Stream Reliability...")
    print("=" * 60)

    recorder = AudioRecorder()

    # Test channels that were having issues
    test_channels = ["36_-_Pacifica", "31_-_SSF"]

    print(
        f"\n🎯 Testing channels: {[recorder.channels[ch]['name'] for ch in test_channels if ch in recorder.channels]}"
    )
    print("\n📊 Enhanced Voice Detection Features:")
    print("  ✅ Signal variance analysis (detects static vs voice)")
    print("  ✅ Zero crossing rate (detects voice patterns)")
    print("  ✅ Entropy analysis (detects signal complexity)")
    print("  ✅ Improved thresholds for voice detection")

    try:
        # Start recording
        for channel in test_channels:
            if channel in recorder.channels:
                print(
                    f"\n🔴 Starting test recording: {recorder.channels[channel]['name']}"
                )
                recorder.start_recording([channel])

        print("\n⏱️ Recording for 90 seconds to test voice detection...")
        print("   Only files with actual voice content should be saved.")

        # Monitor for 90 seconds
        for i in range(18):  # 18 * 5 = 90 seconds
            time.sleep(5)
            print(f"   Recording... {(i + 1) * 5}/90 seconds", end="\r")

        print("\n")

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    finally:
        print("🛑 Stopping test recording...")
        recorder.stop_recording()

        print("\n📋 Test Results Analysis:")

        # Check what files were created
        for channel in test_channels:
            if channel in recorder.channels:
                channel_name = recorder.channels[channel]["name"]
                channel_dir = os.path.join("audio_files", channel)

                if os.path.exists(channel_dir):
                    # Get files from last 5 minutes
                    import glob
                    from datetime import datetime

                    recent_files = []
                    now = datetime.now()

                    for file in glob.glob(os.path.join(channel_dir, "*.mp3")):
                        if "temp_" not in file:  # Skip temp files
                            file_time = os.path.getmtime(file)
                            file_datetime = datetime.fromtimestamp(file_time)
                            if (
                                now - file_datetime
                            ).total_seconds() < 300:  # Last 5 minutes
                                recent_files.append(file)

                    if recent_files:
                        print(f"\n🎵 {channel_name}:")
                        for file in recent_files:
                            size = os.path.getsize(file)
                            print(f"     ✅ {os.path.basename(file)} ({size:,} bytes)")
                    else:
                        print(
                            f"\n🔇 {channel_name}: No voice detected (no files saved)"
                        )
                else:
                    print(f"\n📁 {channel_name}: No recordings directory")

        print("\n" + "=" * 60)
        print("🎉 Voice Detection Test Complete!")
        print("\nNext steps:")
        print("  • Check the saved files to verify they contain actual voice")
        print("  • Files with only static/dead air should have been filtered out")
        print("  • SSF channel should show consistent connection behavior")


if __name__ == "__main__":
    main()
