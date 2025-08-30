# Per-Channel Voice Activity Detection (VAD) Configuration

## Overview

The stream recorder now supports individual VAD (Voice Activity Detection) configuration for each radio channel, allowing fine-tuned transmission detection based on each channel's specific characteristics.

## Configuration Structure

Each channel in `radio_channels.json` can now include a `vad` section with the following parameters:

```json
{
  "name": "Channel Name",
  "url": "stream_url",
  "vad": {
    "energy_threshold": 8e-6,          // Energy level required for speech detection
    "zcr_min": 0.08,                   // Minimum zero-crossing rate for speech
    "zcr_max": 0.32,                   // Maximum zero-crossing rate for speech
    "speech_frames_to_start": 7,       // Consecutive speech frames needed to start recording
    "hang_time_ms": 400,               // Time to continue recording after speech ends
    "min_transmission_ms": 2000,       // Minimum transmission length to save
    "max_transmission_ms": 30000       // Maximum transmission length
  }
}
```

## Parameter Descriptions

### Energy Threshold (`energy_threshold`)
- **Purpose**: Minimum audio energy level to consider for speech detection
- **Range**: `1e-6` to `1e-4` (scientific notation)
- **Lower values**: More sensitive, catches quieter transmissions
- **Higher values**: Less sensitive, reduces false positives
- **Default**: `8e-6`

### Zero-Crossing Rate Range (`zcr_min`, `zcr_max`)
- **Purpose**: Defines the frequency characteristics of human speech
- **Range**: `0.01` to `0.50`
- **Narrower range**: More selective for speech-like audio
- **Wider range**: More permissive, may catch more transmissions
- **Default**: `0.08` to `0.32`

### Speech Frames to Start (`speech_frames_to_start`)
- **Purpose**: Number of consecutive speech-detected frames needed to begin recording
- **Range**: `3` to `10`
- **Lower values**: More responsive, quicker to start recording
- **Higher values**: More stable, reduces false starts
- **Default**: `7` (140ms at 20ms frames)

### Hang Time (`hang_time_ms`)
- **Purpose**: Time to continue recording after speech detection ends
- **Range**: `100ms` to `1000ms`
- **Purpose**: Captures the end of transmissions and brief pauses
- **Default**: `400ms`

### Transmission Length Limits
- **`min_transmission_ms`**: Minimum duration to save a recording (filters out noise)
- **`max_transmission_ms`**: Maximum duration to prevent runaway recordings
- **Typical ranges**: 1000ms to 5000ms for minimum, 30000ms for maximum

## Channel Profiles

### Sensitive Profile (Low Thresholds)
Good for channels with quiet or variable audio:
```json
"vad": {
  "energy_threshold": 6e-6,
  "zcr_min": 0.05,
  "zcr_max": 0.35,
  "speech_frames_to_start": 5,
  "min_transmission_ms": 1500
}
```

### Balanced Profile (Standard)
Good for most channels with normal activity:
```json
"vad": {
  "energy_threshold": 7e-6,
  "zcr_min": 0.06,
  "zcr_max": 0.38,
  "speech_frames_to_start": 6,
  "min_transmission_ms": 1800
}
```

### Strict Profile (High Thresholds)
Good for noisy channels that produce false positives:
```json
"vad": {
  "energy_threshold": 1e-5,
  "zcr_min": 0.08,
  "zcr_max": 0.30,
  "speech_frames_to_start": 8,
  "min_transmission_ms": 2500
}
```

## Current Channel Configurations

### Channels with Custom VAD
1. **CWMA** - Sensitive profile for tactical operations
2. **2 - Sheriff** - Balanced profile with wider ZCR range
3. **18 - EPA** - Strict profile to reduce false positives
4. **30 - San Bruno** - Very strict profile (was problematic)
5. **Fire - Control-1** - Sensitive profile for emergency communications

### Channels Using Defaults
All other channels use the global default settings:
- Energy threshold: `8e-6`
- ZCR range: `0.08` to `0.32`
- Speech frames: `7`
- Minimum transmission: `2000ms`

## Management Tools

### VAD Configuration Validator
```bash
uv run python scripts/validate_vad_config.py
```
- Validates all channel VAD configurations
- Shows which channels have custom settings
- Tests AudioProcessor initialization
- Provides sensitivity analysis

### VAD Performance Monitor
```bash
uv run python scripts/monitor_vad_performance.py
```
- Analyzes recording behavior over the last 30 minutes
- Shows effectiveness of VAD settings per channel
- Provides quality scores and recommendations

## Implementation Details

### AudioProcessor Integration
The `AudioProcessor` class now accepts a `channel_config` parameter:
```python
audio_processor = AudioProcessor(processor_config, channel_config)
```

The channel's VAD settings override global defaults during initialization.

### Backward Compatibility
- Channels without VAD configuration use sensible defaults
- Existing functionality remains unchanged
- Gradual migration to per-channel settings is supported

## Best Practices

1. **Start with defaults**: Only add custom VAD settings for problematic channels
2. **Monitor results**: Use the performance monitor to validate changes
3. **Iterative tuning**: Adjust one parameter at a time and observe results
4. **Channel-specific needs**:
   - **Fire/EMS**: Lower thresholds for emergency communications
   - **Police**: Balanced settings for clear transmissions
   - **Noisy channels**: Higher thresholds to reduce false positives

## Troubleshooting

### Too Many Short Files
- Increase `energy_threshold`
- Increase `min_transmission_ms`
- Increase `speech_frames_to_start`

### Missing Transmissions
- Decrease `energy_threshold`
- Widen ZCR range (`zcr_min` lower, `zcr_max` higher)
- Decrease `speech_frames_to_start`

### False Positives from Noise
- Narrow ZCR range
- Increase `energy_threshold`
- Increase `speech_frames_to_start`

## Future Enhancements

- Automatic VAD parameter optimization based on channel history
- Machine learning-based transmission detection
- Real-time VAD parameter adjustment
- Channel-specific noise profiling
