#!/usr/bin/env python3
"""
Test script to verify transmission filtering improvements
"""

import time
from audio_recorder import AudioRecorder


def main():
    print("🧪 Testing improved transmission detection...")
    print("Starting 60-second test recording on Fire Control-3 and SSF channels")

    recorder = AudioRecorder()

    # Test specific channels that were having issues
    test_channels = ["Fire_-_Control-3", "31_-_SSF"]

    try:
        for channel in test_channels:
            if channel in recorder.channels:
                print(
                    f"✅ Starting test recording: {recorder.channels[channel]['name']}"
                )
                recorder.start_recording([channel])

        print("\n📊 Recording for 60 seconds to test transmission filtering...")
        print("This will test if background noise is properly filtered out.")
        time.sleep(60)

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    finally:
        print("\n🛑 Stopping test recording...")
        recorder.stop_recording()
        print("✅ Test complete!")
        print("\nCheck the audio_files/ directory for results.")
        print(
            "Files should only be created for actual transmissions, not background noise."
        )


if __name__ == "__main__":
    main()
