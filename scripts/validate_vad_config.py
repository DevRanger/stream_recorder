#!/usr/bin/env python3
"""
VAD Configuration Validator
Validates and displays per-channel VAD settings
"""

import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio_processor import AudioProcessor

def load_channels():
    """Load channel configuration"""
    with open('radio_channels.json', 'r') as f:
        data = json.load(f)
    return data['channels']

def validate_vad_config():
    """Validate and display VAD configuration for all channels"""
    channels = load_channels()
    
    print("=== VAD Configuration Validation ===\n")
    
    # Default VAD settings
    default_vad = {
        'energy_threshold': 8e-6,
        'zcr_min': 0.08,
        'zcr_max': 0.32,
        'speech_frames_to_start': 7,
        'hang_time_ms': 400,
        'min_transmission_ms': 2000,
        'max_transmission_ms': 30000
    }
    
    channels_with_vad = 0
    channels_without_vad = 0
    
    for channel in channels:
        name = channel['name']
        has_vad = 'vad' in channel
        
        if has_vad:
            channels_with_vad += 1
            vad_config = channel['vad']
            
            print(f"✅ {name}")
            print(f"   Energy Threshold: {vad_config.get('energy_threshold', default_vad['energy_threshold']):.2e}")
            print(f"   ZCR Range: {vad_config.get('zcr_min', default_vad['zcr_min']):.2f} - {vad_config.get('zcr_max', default_vad['zcr_max']):.2f}")
            print(f"   Speech Frames: {vad_config.get('speech_frames_to_start', default_vad['speech_frames_to_start'])}")
            print(f"   Min Transmission: {vad_config.get('min_transmission_ms', default_vad['min_transmission_ms'])}ms")
            print(f"   Hang Time: {vad_config.get('hang_time_ms', default_vad['hang_time_ms'])}ms")
            
            # Test AudioProcessor initialization
            try:
                processor = AudioProcessor(channel_config=channel)
                print(f"   ✅ AudioProcessor initialization: SUCCESS")
                print(f"      Actual energy threshold: {processor.energy_threshold:.2e}")
                print(f"      Actual ZCR range: {processor.zcr_min:.2f} - {processor.zcr_max:.2f}")
                print(f"      Actual min transmission: {processor.min_transmission_ms}ms")
            except Exception as e:
                print(f"   ❌ AudioProcessor initialization: FAILED - {e}")
            
        else:
            channels_without_vad += 1
            print(f"⚠️  {name} (using defaults)")
            
            # Test with defaults
            try:
                processor = AudioProcessor(channel_config=channel)
                print(f"   Default energy threshold: {processor.energy_threshold:.2e}")
                print(f"   Default ZCR range: {processor.zcr_min:.2f} - {processor.zcr_max:.2f}")
                print(f"   Default min transmission: {processor.min_transmission_ms}ms")
            except Exception as e:
                print(f"   ❌ AudioProcessor initialization: FAILED - {e}")
        
        print()
    
    print(f"Summary:")
    print(f"  Channels with custom VAD: {channels_with_vad}")
    print(f"  Channels using defaults: {channels_without_vad}")
    print(f"  Total channels: {len(channels)}")
    
    # Show channels by sensitivity level
    print(f"\n=== VAD Sensitivity Analysis ===")
    
    sensitive_channels = []
    normal_channels = []
    strict_channels = []
    
    for channel in channels:
        if 'vad' not in channel:
            continue
            
        vad = channel['vad']
        energy_threshold = vad.get('energy_threshold', default_vad['energy_threshold'])
        min_transmission = vad.get('min_transmission_ms', default_vad['min_transmission_ms'])
        
        if energy_threshold < 7e-6 and min_transmission < 2000:
            sensitive_channels.append(channel['name'])
        elif energy_threshold > 9e-6 or min_transmission > 2200:
            strict_channels.append(channel['name'])
        else:
            normal_channels.append(channel['name'])
    
    print(f"Sensitive (low thresholds): {', '.join(sensitive_channels) if sensitive_channels else 'None'}")
    print(f"Normal (balanced): {', '.join(normal_channels) if normal_channels else 'None'}")
    print(f"Strict (high thresholds): {', '.join(strict_channels) if strict_channels else 'None'}")

if __name__ == '__main__':
    validate_vad_config()
