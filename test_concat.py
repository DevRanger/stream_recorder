#!/usr/bin/env python3
"""
Test script to debug the concatenation endpoint
"""

import requests
import json
import sys

def test_concatenation():
    """Test the concatenation endpoint"""
    
    url = "http://localhost:8000/api/concatenate"
    headers = {"Content-Type": "application/json"}
    data = {
        "files": [
            "20250828_150445_160_2_-_Sheriff.flac",
            "20250828_150631_693_2_-_Sheriff.flac"
        ]
    }
    
    print("Testing concatenation endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Response JSON: {json.dumps(result, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
        else:
            print(f"Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    
    return response.status_code == 200

def test_status():
    """Test the status endpoint first"""
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=5)
        print(f"Status endpoint: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Status endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Flask API endpoints...")
    
    if test_status():
        print("✅ Status endpoint working")
        test_concatenation()
    else:
        print("❌ Status endpoint not working - Flask may not be running")
        sys.exit(1)
