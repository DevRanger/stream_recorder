#!/usr/bin/env python3
"""Quick test to validate timestamp extraction logic"""

def extract_timestamp(filename):
    """Extract timestamp from filename (YYYYMMDD_HHMMSS_*)"""
    # Handle both formats: "YYYYMMDD_HHMMSS_*" and "temp_YYYYMMDD_HHMMSS_*"
    parts = filename.split('_')
    if parts[0] == 'temp' and len(parts) >= 3:
        # temp_YYYYMMDD_HHMMSS_* format
        timestamp_str = parts[1] + '_' + parts[2]
    elif len(parts) >= 2:
        # YYYYMMDD_HHMMSS_* format
        timestamp_str = parts[0] + '_' + parts[1]
    else:
        return None  # Skip files with unexpected naming format
    return timestamp_str

# Test cases
test_files = [
    "temp_20250825_113225_786_CalTrain.mp3",
    "20250825_112413_241_CalTrain.mp3",
    "temp_20250825_112818_866_28_-_Burlingame.mp3",
    "20250825_120000_000_Test.mp3"
]

print("Testing timestamp extraction:")
for filename in test_files:
    timestamp = extract_timestamp(filename)
    print(f"{filename} -> {timestamp}")
