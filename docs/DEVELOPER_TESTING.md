# Developer Quick Reference - Preferred Test Channels

## Test Channels for Audio Processing

When testing the audio processing pipeline, always use these specific channels for consistent and reliable results:

### Primary Test Channels

```python
# Channel IDs for testing
TEST_CHANNELS = {
    'ssf': '31_-_SSF',           # South San Francisco
    'epa': '18_-_EPA',           # East Palo Alto  
    'san_mateo': '25_-_San_Mateo', # San Mateo
    'daly_city': '35_-_Daly_City'  # Daly City
}
```

### Quick Testing Examples

```python
# Single channel test (use SSF as primary)
test_channels = ['31_-_SSF']

# Multi-channel test (use SSF + EPA)
test_channels = ['31_-_SSF', '18_-_EPA']

# Full test (all four preferred channels)
test_channels = ['31_-_SSF', '18_-_EPA', '25_-_San_Mateo', '35_-_Daly_City']
```

### Test Utility Usage

```bash
# Quick 5-second test with SSF
uv run python dev/test_audio_processing.py quick

# Standard 10-second test with SSF + EPA  
uv run python dev/test_audio_processing.py standard

# Full comprehensive test with all preferred channels
uv run python dev/test_audio_processing.py full

# Test specific channel
uv run python dev/test_audio_processing.py single ssf
uv run python dev/test_audio_processing.py single epa
```

### Manual Testing Template

```python
from audio_recorder import AudioRecorder
import time

# Initialize recorder
recorder = AudioRecorder()

# Test with preferred channels
test_channels = ['31_-_SSF', '18_-_EPA']  # SSF + EPA

# Start recording
recorder.start_recording(test_channels)
print(f"Recording {len(test_channels)} channels...")

# Record for test duration
time.sleep(10)  # 10 seconds

# Stop recording
recorder.stop_recording()
print("Test completed")
```

### Why These Channels?

- **31_-_SSF**: Reliable primary test channel with moderate traffic
- **18_-_EPA**: Good for testing rapid-fire transmissions  
- **25_-_San_Mateo**: Mixed transmission lengths for comprehensive testing
- **35_-_Daly_City**: Variable signal quality for noise handling tests

These channels provide good coverage of different transmission patterns and audio characteristics for thorough testing of the audio processing pipeline.
