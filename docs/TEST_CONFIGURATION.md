# Test Configuration for Audio Processing

## Preferred Test Channels

For testing the audio processing pipeline, use these specific channels that provide good variety in transmission patterns and audio characteristics:

### Primary Test Channels

1. **31 - SSF (South San Francisco)**
   - Channel ID: `31_-_SSF`
   - Characteristics: Moderate traffic, clear audio
   - Good for: General VAD testing, transmission detection

2. **18 - EPA (East Palo Alto)**
   - Channel ID: `18_-_EPA`
   - Characteristics: Variable traffic patterns
   - Good for: Rapid-fire detection, quick acknowledgments

3. **25 - San Mateo**
   - Channel ID: `25_-_San_Mateo`
   - Characteristics: Mixed transmission lengths
   - Good for: Long conversation testing, audio quality

4. **35 - Daly City**
   - Channel ID: `35_-_Daly_City`
   - Characteristics: Varied signal quality
   - Good for: Noise handling, AGC testing

## Test Configuration Examples

### Quick Test (Single Channel)
```python
test_channels = ['31_-_SSF']  # SSF for basic functionality
```

### Standard Test (Two Channels)
```python
test_channels = ['31_-_SSF', '18_-_EPA']  # SSF + EPA for variety
```

### Full Test (All Four Channels)
```python
test_channels = ['31_-_SSF', '18_-_EPA', '25_-_San_Mateo', '35_-_Daly_City']
```

## Test Scenarios

### Audio Processing Tests
```python
# Test with different configurations
test_configs = {
    'high_quality': {
        'enable_filtering': True,
        'enable_denoise': True,
        'vad_aggressiveness': 3
    },
    'balanced': {
        'enable_filtering': True,
        'enable_denoise': False,
        'vad_aggressiveness': 2
    },
    'performance': {
        'enable_filtering': False,
        'enable_denoise': False,
        'vad_aggressiveness': 1
    }
}
```

### Detection Sensitivity Tests
```python
# Test transmission detection with different settings
detection_tests = {
    'sensitive': {
        'speech_frames_to_start': 2,
        'min_transmission_ms': 200,
        'hang_time_ms': 400
    },
    'balanced': {
        'speech_frames_to_start': 3,
        'min_transmission_ms': 300,
        'hang_time_ms': 500
    },
    'conservative': {
        'speech_frames_to_start': 4,
        'min_transmission_ms': 500,
        'hang_time_ms': 600
    }
}
```

## Usage in Code

Update test scripts to use these channels:

```python
# In audio_recorder.py testing
test_channels = ['31_-_SSF', '18_-_EPA', '25_-_San_Mateo', '35_-_Daly_City']

# In quick tests
quick_test_channel = '31_-_SSF'  # SSF as primary test channel
```
