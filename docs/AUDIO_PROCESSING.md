# Advanced Audio Processing Guide

## Overview

The Radio Stream Recorder now features a completely redesigned audio processing pipeline that provides professional-grade Voice Activity Detection (VAD), audio filtering, and transmission detection. This new system processes audio in real-time with minimal latency while providing superior transmission detection accuracy.

## New Processing Pipeline

### 1. MP3 Stream Ingestion
- **Direct MP3 decoding**: Streams are decoded to PCM in memory without temporary files
- **Automatic downmixing**: Multi-channel audio is automatically converted to mono
- **Format normalization**: Audio is normalized to [-1, 1] range for consistent processing

### 2. Resampling & Preprocessing
- **Target sample rate**: 16 kHz (optimal for VAD) or 8 kHz for narrowband
- **High-pass filtering**: 150-200 Hz (removes hum, CTCSS/PL tones)
- **Low-pass filtering**: 4-5 kHz (speech band optimization)
- **Optional denoising**: Light spectral gate for noise reduction
- **Mild AGC**: Automatic Gain Control for consistent levels

### 3. Voice Activity Detection (VAD)
- **Frame-based processing**: 20ms frames for real-time analysis
- **Hysteresis logic**: Requires multiple speech frames to start detection
- **Hang time**: Configurable delay before ending transmission
- **Pre-roll buffer**: Captures audio before speech detection starts
- **Min/max length enforcement**: Filters out noise bursts and overly long segments

### 4. Archival Recording
- **FLAC format**: Lossless compression for long-term storage
- **Rich metadata**: Channel, timestamp, processing version info
- **Quality preservation**: No re-encoding artifacts

## Configuration Options

### Global Audio Processing Settings

These settings apply to all channels unless overridden:

```python
audio_processor_config = {
    'target_sample_rate': 16000,      # 16kHz for optimal VAD
    'frame_duration_ms': 20,          # 20ms frame processing
    'enable_filtering': True,         # Enable HP/LP filtering
    'highpass_freq': 200,             # 200Hz highpass filter
    'lowpass_freq': 4000,             # 4kHz lowpass filter
    'enable_denoise': False,          # Denoise (disabled by default)
    'enable_agc': True,               # Automatic Gain Control
    'agc_target_level': -20,          # Target level (-20dB)
    'vad_aggressiveness': 2,          # VAD sensitivity (0-3)
    'speech_frames_to_start': 3,      # Frames needed to start (60ms)
    'hang_time_ms': 500,              # Hang time (500ms)
    'preroll_ms': 250,                # Pre-roll buffer (250ms)
    'min_transmission_ms': 300,       # Minimum transmission (300ms)
    'max_transmission_ms': 30000,     # Maximum transmission (30s)
}
```

### Per-Channel Configuration

Individual channels can override global settings by including an `audio_processing` section:

```json
{
  "channel_id": {
    "name": "Channel Name",
    "url": "http://stream.url",
    "enabled": true,
    "group": "Group",
    "audio_processing": {
      "highpass_freq": 150,
      "enable_denoise": true,
      "vad_aggressiveness": 3,
      "hang_time_ms": 600,
      "min_transmission_ms": 200
    }
  }
}
```

## Parameter Tuning Guide

### Sample Rate Selection
- **16 kHz**: Recommended for most applications (optimal VAD performance)
- **8 kHz**: For narrowband systems or resource-constrained environments

### Filtering Parameters
- **High-pass frequency (150-200 Hz)**:
  - 150 Hz: More lenient, preserves deep voices
  - 200 Hz: Stricter, better CTCSS/hum removal
- **Low-pass frequency (4000-5000 Hz)**:
  - 4000 Hz: Standard speech band
  - 5000 Hz: Preserves more high-frequency content

### VAD Parameters
- **Aggressiveness (0-3)**:
  - 0: Least aggressive (may include more noise)
  - 1: Mild (good for clean environments)
  - 2: Moderate (recommended default)
  - 3: Most aggressive (strict speech detection)

- **Speech frames to start (1-5)**:
  - 1-2: Very responsive (may trigger on noise)
  - 3: Balanced (recommended)
  - 4-5: Conservative (may miss quick transmissions)

- **Hang time (300-800 ms)**:
  - 300 ms: Quick cutoff (may truncate slow speakers)
  - 500 ms: Balanced (recommended)
  - 800 ms: Extended (captures pauses in speech)

### Transmission Length Limits
- **Minimum (200-500 ms)**:
  - 200 ms: Captures very brief acknowledgments
  - 300 ms: Standard minimum (recommended)
  - 500 ms: Conservative (filters out most noise)

- **Maximum (20-60 seconds)**:
  - 20s: Prevents very long recordings
  - 30s: Balanced (recommended)
  - 60s: Allows extended conversations

## Quality vs Performance Trade-offs

### High Quality Settings (More CPU intensive)
```json
{
  "target_sample_rate": 16000,
  "enable_filtering": true,
  "enable_denoise": true,
  "enable_agc": true,
  "vad_aggressiveness": 2,
  "speech_frames_to_start": 2,
  "preroll_ms": 300
}
```

### Balanced Settings (Recommended)
```json
{
  "target_sample_rate": 16000,
  "enable_filtering": true,
  "enable_denoise": false,
  "enable_agc": true,
  "vad_aggressiveness": 2,
  "speech_frames_to_start": 3,
  "preroll_ms": 250
}
```

### Performance Settings (Lower CPU usage)
```json
{
  "target_sample_rate": 8000,
  "enable_filtering": false,
  "enable_denoise": false,
  "enable_agc": false,
  "vad_aggressiveness": 1,
  "speech_frames_to_start": 2,
  "preroll_ms": 200
}
```

## Channel-Specific Optimization

### High-Traffic Channels
For busy dispatch channels with rapid-fire communications:
```json
{
  "speech_frames_to_start": 2,
  "hang_time_ms": 400,
  "min_transmission_ms": 200,
  "vad_aggressiveness": 3
}
```

### Low-Traffic Channels
For occasional-use channels or tactical frequencies:
```json
{
  "speech_frames_to_start": 3,
  "hang_time_ms": 600,
  "min_transmission_ms": 500,
  "vad_aggressiveness": 2
}
```

### Noisy Environments
For channels with poor signal quality:
```json
{
  "enable_denoise": true,
  "enable_agc": true,
  "highpass_freq": 200,
  "vad_aggressiveness": 3,
  "speech_frames_to_start": 4
}
```

## Migration from Legacy System

### File Format Changes
- **Old**: MP3 files with potential re-encoding artifacts
- **New**: FLAC files with lossless quality preservation
- **Compatibility**: Both formats are supported in the web interface

### Detection Improvements
- **Old**: Simple silence-based detection with fixed thresholds
- **New**: Advanced VAD with adaptive processing and hysteresis
- **Result**: Significantly better transmission detection accuracy

### Performance Impact
- **Processing**: Slightly higher CPU usage for much better quality
- **Storage**: FLAC files are larger but provide better archival quality
- **Latency**: Real-time processing with minimal delay

## Troubleshooting

### Common Issues

**Too many false positives (noise detected as speech)**:
- Increase `vad_aggressiveness` to 3
- Increase `speech_frames_to_start` to 4-5
- Increase `min_transmission_ms` to 500
- Enable `enable_denoise`

**Missing short transmissions**:
- Decrease `speech_frames_to_start` to 2
- Decrease `min_transmission_ms` to 200
- Increase `hang_time_ms` to 600
- Decrease `vad_aggressiveness` to 1-2

**Truncated transmissions**:
- Increase `hang_time_ms` to 800
- Increase `preroll_ms` to 300
- Check if `max_transmission_ms` is too low

**Poor audio quality**:
- Enable `enable_agc` for level normalization
- Adjust `agc_target_level` to -18 or -16 dB
- Enable `enable_filtering` for better speech clarity

### Performance Monitoring

Check logs for processing statistics:
```
INFO:audio_processor:Completed transmission: 1240ms
INFO:audio_recorder:Saved FLAC transmission: /path/to/file.flac (1240ms)
```

Monitor CPU usage and adjust settings if needed:
- Disable denoise if CPU usage is high
- Use 8kHz sample rate for lower-powered systems
- Reduce frame processing frequency

## Advanced Features

### Custom VAD Implementation
The system uses a fallback energy-based VAD when WebRTC VAD is unavailable. This can be customized by modifying the `simple_vad()` method in `AudioProcessor`.

### Metadata Enhancement
FLAC files include rich metadata that can be extended for specific use cases:
- Channel/talkgroup information
- Signal strength measurements
- Processing version tracking
- Custom application data

### Real-time Monitoring
The new pipeline provides real-time feedback on:
- Transmission detection events
- Audio level statistics
- Processing performance metrics
- VAD decision history

## Web UI Playback Compatibility

### FLAC File Support
The web interface now fully supports FLAC file playback with automatic format detection:

- **Browser compatibility**: Modern browsers (Chrome 56+, Firefox 51+, Safari 11+) support FLAC natively
- **Automatic fallback**: The system provides multiple audio source formats for maximum compatibility
- **Metadata integration**: FLAC metadata is displayed in the web interface
- **Batch playback**: Multiple FLAC files can be queued and played sequentially

### Supported Audio Formats
- **FLAC**: Primary format for new recordings (lossless, with metadata)
- **MP3**: Legacy format support maintained for older recordings
- **Automatic detection**: File extension determines the appropriate MIME type and audio sources

### Testing FLAC Playback
Use the included test page to verify FLAC support in your browser:
```
http://localhost:8000/test_flac_playback.html
```

This test page checks:
- Browser FLAC codec support
- API endpoint functionality
- Audio loading and playback
- Fallback compatibility

This advanced processing system provides professional-grade audio handling while maintaining the simplicity and reliability of the original system.
