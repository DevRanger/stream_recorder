#!/usr/bin/env python3
"""
Debug script to test recording a single channel and see what's happening
"""

import logging
import time
from audio_recorder import AudioRecorder

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    print("🔍 Starting debug recording session...")

    # Initialize audio recorder
    recorder = AudioRecorder()

    # Pick a single active channel for testing
    test_channel = "18_-_EPA"  # EPA channel

    if test_channel not in recorder.channels:
        print(f"❌ Channel {test_channel} not found!")
        return

    print(f"📻 Testing channel: {recorder.channels[test_channel]['name']}")
    print(f"🌐 URL: {recorder.channels[test_channel]['url']}")

    # Start recording for just this channel
    print("🔴 Starting recording...")
    recorder.start_recording([test_channel])

    # Let it record for a short time
    print("⏱️  Recording for 70 seconds to ensure one complete segment...")
    for i in range(7):
        time.sleep(10)
        print(f"⏱️  {(i + 1) * 10} seconds elapsed...")

        # Check if still recording
        if not recorder.is_recording.get(test_channel, False):
            print(f"⚠️  Recording stopped unexpectedly for {test_channel}!")
            break

    # Stop recording
    print("🛑 Stopping recording...")
    recorder.stop_recording([test_channel])

    print("✅ Debug session complete!")


if __name__ == "__main__":
    main()
