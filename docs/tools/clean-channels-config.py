#!/usr/bin/env python3
"""
Clean radio_channels.json by removing unused fields.
Removes: color, tag, and individual noiseGate parameters (threshold, ratio, attack, release)
Keeps: name, url, enabled, group, gain, and noiseGate.enabled only
"""

import json
import sys
import os

def clean_channels_config(input_file, output_file=None):
    """Clean unused fields from radio channels configuration"""
    
    if output_file is None:
        output_file = input_file
    
    try:
        # Read the original file
        with open(input_file, 'r') as f:
            config = json.load(f)
        
        # Clean each channel
        cleaned_channels = []
        for channel in config.get('channels', []):
            cleaned_channel = {
                'name': channel.get('name', ''),
                'url': channel.get('url', ''),
                'enabled': channel.get('enabled', True),
                'group': channel.get('group', 'Unknown'),
                'gain': channel.get('gain', 1.0)
            }
            
            # Only keep noiseGate.enabled if it exists
            noise_gate = channel.get('noiseGate', {})
            if noise_gate:
                cleaned_channel['noiseGate'] = {
                    'enabled': noise_gate.get('enabled', True)
                }
            
            cleaned_channels.append(cleaned_channel)
        
        # Create cleaned configuration
        cleaned_config = {
            'channels': cleaned_channels
        }
        
        # Write the cleaned file
        with open(output_file, 'w') as f:
            json.dump(cleaned_config, f, indent=2)
        
        print(f"✅ Cleaned {len(cleaned_channels)} channels")
        print(f"📝 Removed unused fields: color, tag, noiseGate parameters")
        print(f"💾 Saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning channels: {e}")
        return False

if __name__ == "__main__":
    input_file = "radio_channels.json"
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    # Create backup
    backup_file = f"{input_file}.backup"
    with open(input_file, 'r') as src, open(backup_file, 'w') as dst:
        dst.write(src.read())
    print(f"📦 Created backup: {backup_file}")
    
    # Clean the file
    if clean_channels_config(input_file):
        print("🎉 Cleanup completed successfully!")
    else:
        print("❌ Cleanup failed!")
        sys.exit(1)
