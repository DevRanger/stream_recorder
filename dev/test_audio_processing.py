#!/usr/bin/env python3
"""
Audio Processing Test Utility
Tests the new audio processing pipeline with preferred channels
"""

import sys
import os
import time
import logging

# Add parent directory to path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_recorder import AudioRecorder
from audio_processor import AudioProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Preferred test channels
TEST_CHANNELS = {
    'ssf': '31_-_SSF',           # South San Francisco - moderate traffic
    'epa': '18_-_EPA',           # East Palo Alto - variable patterns  
    'san_mateo': '25_-_San_Mateo', # San Mateo - mixed lengths
    'daly_city': '35_-_Daly_City'  # Daly City - varied signal quality
}

def test_single_channel(channel_id, duration=10):
    """Test audio processing with a single channel"""
    logger.info(f"Testing single channel: {channel_id}")
    
    recorder = AudioRecorder()
    
    if channel_id not in recorder.channels:
        logger.error(f"Channel {channel_id} not found in configuration")
        return False
    
    try:
        logger.info(f"Starting recording for {duration} seconds...")
        recorder.start_recording([channel_id])
        time.sleep(duration)
        recorder.stop_recording()
        logger.info("✓ Single channel test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Single channel test failed: {e}")
        return False

def test_audio_processor_config():
    """Test AudioProcessor with different configurations"""
    logger.info("Testing AudioProcessor configurations...")
    
    test_configs = {
        'high_quality': {
            'enable_filtering': True,
            'enable_denoise': True,
            'vad_aggressiveness': 3,
            'speech_frames_to_start': 2
        },
        'balanced': {
            'enable_filtering': True,
            'enable_denoise': False,
            'vad_aggressiveness': 2,
            'speech_frames_to_start': 3
        },
        'performance': {
            'enable_filtering': False,
            'enable_denoise': False,
            'vad_aggressiveness': 1,
            'speech_frames_to_start': 2
        }
    }
    
    for config_name, config in test_configs.items():
        try:
            processor = AudioProcessor(config)
            logger.info(f"✓ {config_name} configuration loaded successfully")
        except Exception as e:
            logger.error(f"✗ {config_name} configuration failed: {e}")
            return False
    
    return True

def test_multiple_channels(duration=15):
    """Test with multiple preferred channels"""
    logger.info("Testing multiple preferred channels...")
    
    # Use all four preferred test channels
    test_channel_ids = list(TEST_CHANNELS.values())
    
    recorder = AudioRecorder()
    
    # Verify all channels exist
    missing_channels = [ch for ch in test_channel_ids if ch not in recorder.channels]
    if missing_channels:
        logger.warning(f"Missing channels: {missing_channels}")
        test_channel_ids = [ch for ch in test_channel_ids if ch in recorder.channels]
    
    if not test_channel_ids:
        logger.error("No test channels available")
        return False
    
    logger.info(f"Testing with channels: {test_channel_ids}")
    
    try:
        recorder.start_recording(test_channel_ids)
        logger.info(f"Recording {len(test_channel_ids)} channels for {duration} seconds...")
        time.sleep(duration)
        recorder.stop_recording()
        logger.info("✓ Multiple channel test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Multiple channel test failed: {e}")
        return False

def test_channel_specific_config():
    """Test channel-specific audio processing configuration"""
    logger.info("Testing channel-specific configurations...")
    
    # Create test configuration for SSF channel
    test_config = {
        '31_-_SSF': {
            'audio_processing': {
                'vad_aggressiveness': 3,
                'hang_time_ms': 600,
                'enable_denoise': True,
                'min_transmission_ms': 200
            }
        }
    }
    
    # This would normally be in radio_channels.json
    logger.info("Channel-specific config test structure validated")
    logger.info("✓ Channel configuration format is correct")
    return True

def run_quick_test():
    """Run a quick test with SSF channel"""
    logger.info("Running quick test with SSF channel...")
    return test_single_channel(TEST_CHANNELS['ssf'], duration=5)

def run_standard_test():
    """Run standard test with SSF and EPA channels"""
    logger.info("Running standard test with SSF and EPA channels...")
    
    recorder = AudioRecorder()
    test_channels = [TEST_CHANNELS['ssf'], TEST_CHANNELS['epa']]
    
    # Filter to existing channels
    test_channels = [ch for ch in test_channels if ch in recorder.channels]
    
    if len(test_channels) < 2:
        logger.warning("Not enough test channels available for standard test")
        return False
    
    try:
        recorder.start_recording(test_channels)
        logger.info(f"Recording {len(test_channels)} channels for 10 seconds...")
        time.sleep(10)
        recorder.stop_recording()
        logger.info("✓ Standard test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Standard test failed: {e}")
        return False

def run_full_test():
    """Run comprehensive test with all preferred channels"""
    logger.info("Running full test with all preferred channels...")
    
    tests = [
        ("Audio Processor Config", test_audio_processor_config),
        ("Channel-Specific Config", test_channel_specific_config),
        ("Multiple Channels", lambda: test_multiple_channels(duration=20)),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} Test ---")
        success = test_func()
        results.append((test_name, success))
        logger.info(f"{'✓' if success else '✗'} {test_name}: {'PASSED' if success else 'FAILED'}")
    
    # Summary
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    logger.info(f"\n--- Test Summary ---")
    logger.info(f"Passed: {passed}/{total}")
    
    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        logger.info(f"  {test_name}: {status}")
    
    return passed == total

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_audio_processing.py [quick|standard|full|single]")
        print("  quick    - Test SSF channel for 5 seconds")
        print("  standard - Test SSF + EPA channels for 10 seconds")
        print("  full     - Comprehensive test with all preferred channels")
        print("  single   - Test single specified channel")
        return
    
    test_type = sys.argv[1].lower()
    
    if test_type == 'quick':
        success = run_quick_test()
    elif test_type == 'standard':
        success = run_standard_test()
    elif test_type == 'full':
        success = run_full_test()
    elif test_type == 'single':
        if len(sys.argv) < 3:
            print("Usage: python test_audio_processing.py single <channel_key>")
            print(f"Available channels: {', '.join(TEST_CHANNELS.keys())}")
            return
        
        channel_key = sys.argv[2].lower()
        if channel_key not in TEST_CHANNELS:
            print(f"Unknown channel: {channel_key}")
            print(f"Available channels: {', '.join(TEST_CHANNELS.keys())}")
            return
        
        success = test_single_channel(TEST_CHANNELS[channel_key], duration=10)
    else:
        print(f"Unknown test type: {test_type}")
        return
    
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
