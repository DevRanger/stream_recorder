#!/usr/bin/env python3
"""
Debug script to test audio quality with and without noise gate
"""

import logging
import time
import os
from audio_recorder import AudioRecorder

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    print("🔍 Testing audio quality with and without noise gate...")

    # Initialize audio recorder
    recorder = AudioRecorder()

    # Test EPA channel
    test_channel = "18_-_EPA"

    if test_channel not in recorder.channels:
        print(f"❌ Channel {test_channel} not found!")
        return

    print(f"📻 Testing channel: {recorder.channels[test_channel]['name']}")

    # First, disable noise gate temporarily
    original_noise_gate = recorder.channels[test_channel]["noise_gate"].copy()
    print(f"🔧 Original noise gate: {original_noise_gate}")

    # Test 1: Record WITHOUT noise gate
    print("\n🎵 Test 1: Recording WITHOUT noise gate...")
    recorder.channels[test_channel]["noise_gate"]["enabled"] = False

    recorder.start_recording([test_channel])
    print("⏱️  Recording for 70 seconds...")
    time.sleep(70)
    recorder.stop_recording([test_channel])

    # Test 2: Record WITH noise gate
    print("\n🔊 Test 2: Recording WITH noise gate...")
    recorder.channels[test_channel]["noise_gate"] = original_noise_gate

    recorder.start_recording([test_channel])
    print("⏱️  Recording for 70 seconds...")
    time.sleep(70)
    recorder.stop_recording([test_channel])

    print("✅ Tests complete! Compare the audio files to see the difference.")
    print("📁 Check audio_files/18_-_EPA/ for the recorded files")


if __name__ == "__main__":
    main()
