#!/usr/bin/env python3
"""
Test script for the improved voice detection features
"""

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_recorder import AudioRecorder
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
import numpy as np

def create_test_audio():
    """Create test audio segments for testing voice detection"""
    
    # Create silence (1 second)
    silence = AudioSegment.silent(duration=1000)
    
    # Create white noise (low level)
    noise = WhiteNoise().to_audio_segment(duration=1000) - 20  # Quiet noise
    
    # Create a synthetic voice-like signal (multiple tones with speech-like characteristics)
    # Human speech typically has fundamental frequencies between 80-300 Hz
    voice_segment = AudioSegment.silent(duration=2000)
    
    # Add multiple harmonics to simulate voice
    for freq in [150, 300, 450, 600]:  # Fundamental + harmonics
        tone = Sine(freq).to_audio_segment(duration=2000)
        # Vary amplitude to simulate speech patterns
        tone = tone - 15  # Reduce volume
        # Add some amplitude modulation to simulate speech
        samples = np.array(tone.get_array_of_samples(), dtype=np.float32)
        # Simple amplitude modulation at 4 Hz (speech rate)
        t = np.linspace(0, 2, len(samples))
        modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)
        modulated_samples = samples * modulation
        
        # Convert back to AudioSegment
        modulated_tone = tone._spawn(modulated_samples.astype(np.int16).tobytes())
        voice_segment = voice_segment.overlay(modulated_tone)
    
    return {
        'silence': silence,
        'noise': noise,
        'voice': voice_segment
    }

def test_voice_detection():
    """Test the voice detection algorithm"""
    
    print("Testing improved voice detection...")
    
    # Initialize recorder
    recorder = AudioRecorder()
    
    # Create test audio
    test_audio = create_test_audio()
    
    print("\n=== Voice Detection Test Results ===")
    
    for name, audio in test_audio.items():
        print(f"\nTesting {name}:")
        print(f"  Duration: {len(audio)}ms")
        print(f"  Max dBFS: {audio.max_dBFS:.1f}")
        print(f"  RMS dBFS: {audio.dBFS:.1f}")
        
        # Test voice detection
        has_voice, reason = recorder.has_voice_activity(audio)
        print(f"  Voice detected: {has_voice}")
        print(f"  Reason: {reason}")
        
        # Test individual components
        zcr = recorder.calculate_zero_crossing_rate(audio)
        spectral_var = recorder.calculate_spectral_variance(audio)
        print(f"  Zero crossing rate: {zcr:.1f} Hz")
        print(f"  Spectral variance: {spectral_var:.3f}")
        
        # Test silence trimming
        start_ms, end_ms, trim_reason = recorder.trim_silence_timestamps(audio, 0, len(audio))
        if start_ms is not None:
            trimmed_duration = end_ms - start_ms
            print(f"  After trimming: {trimmed_duration}ms ({trim_reason})")
        else:
            print(f"  Trimming result: {trim_reason}")

if __name__ == "__main__":
    test_voice_detection()
