#!/usr/bin/env python3
"""
Test script to check if API endpoints are working
"""
import requests
import json

def test_api():
    base_url = "http://localhost:8080"
    
    endpoints = [
        "/api/health",
        "/api/channels", 
        "/api/status",
        "/api/stats"
    ]
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            print(f"Testing {url}...")
            response = requests.get(url, timeout=5)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"Error: {response.text}")
            print("-" * 50)
        except requests.exceptions.RequestException as e:
            print(f"Connection error for {endpoint}: {e}")
        except Exception as e:
            print(f"Error testing {endpoint}: {e}")

if __name__ == "__main__":
    test_api()
