#!/usr/bin/env python3
"""
Test channel connectivity and identify issues
"""

import requests
import sys

def test_channels():
    """Test all channels via the API"""
    try:
        print("Testing channel connectivity...\n")
        
        # Test connectivity via API
        response = requests.get('http://localhost:8000/api/test-connectivity')
        if response.status_code != 200:
            print(f"Error accessing API: {response.status_code}")
            return
        
        data = response.json()
        if data['status'] != 'success':
            print(f"API error: {data.get('message', 'Unknown error')}")
            return
        
        results = data['results']
        
        # Categorize results
        working = []
        failed = []
        
        for channel_id, result in results.items():
            if result['accessible']:
                working.append((channel_id, result))
            else:
                failed.append((channel_id, result))
        
        # Display results
        print(f"✅ Working channels ({len(working)}):")
        for channel_id, result in working:
            print(f"  {result['name']} - {result['content_type']}")
        
        print(f"\n❌ Failed channels ({len(failed)}):")
        for channel_id, result in failed:
            error_info = result.get('error', f"HTTP {result.get('status_code', 'Unknown')}")
            print(f"  {result['name']} - {error_info}")
            print(f"    URL: {result['url']}")
        
        print(f"\nSummary: {len(working)} working, {len(failed)} failed")
        
        if failed:
            print("\nChannels with issues should be investigated or temporarily disabled.")
            
    except Exception as e:
        print(f"Error testing channels: {e}")

if __name__ == '__main__':
    test_channels()
