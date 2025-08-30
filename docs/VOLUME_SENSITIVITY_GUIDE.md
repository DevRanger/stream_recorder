# Volume Sensitivity Configuration Guide

## Overview

The Stream Recorder uses a simple but effective audio level detection system based on RMS (Root Mean Square) analysis. The `volume_sensitivity` setting in `radio_channels.json` controls when audio is detected as a transmission.

## How It Works

### RMS Level Detection

1. **Audio Processing**: Stream audio is analyzed in 100ms chunks
2. **RMS Calculation**: Each chunk's RMS level is calculated (amplitude measure)
3. **Threshold Comparison**: RMS level is compared against `volume_sensitivity`
4. **Detection**: If RMS > threshold, audio is marked as "active"
5. **Segmentation**: Active chunks are merged and filtered by length

### Audio Flow

```
Stream → 100ms chunks → RMS calculation → Threshold test → Segment detection → FLAC output
```

## Configuration Values

### Range and Meaning

- **Valid range**: 0.001 to 0.1
- **Typical range**: 0.005 to 0.02
- **Units**: RMS amplitude (not dB)

### Sensitivity Levels

| Value Range | Sensitivity | Use Case | Examples |
|-------------|-------------|----------|----------|
| 0.001-0.003 | Very High | Quiet channels, distant signals | Tac channels, background chatter |
| 0.004-0.008 | High | Active channels with clear audio | Sheriff, CHP, busy fire |
| 0.009-0.015 | Medium | Standard channels | Most city police/fire |
| 0.016-0.025 | Low | Channels with strong signals only | Control frequencies |
| 0.026+ | Very Low | Emergency/test use only | High-power repeaters |

## Channel-Specific Settings

### Current Optimized Values

These settings have been tested and optimized:

```json
{
  "name": "25 - San Mateo",
  "volume_sensitivity": 0.005,
  "note": "Very active, needs sensitive detection"
}

{
  "name": "2 - Sheriff", 
  "volume_sensitivity": 0.008,
  "note": "Active with clear audio"
}

{
  "name": "CHP",
  "volume_sensitivity": 0.008, 
  "note": "Highway patrol, clear signals"
}

{
  "name": "20 - Menlo Park",
  "volume_sensitivity": 0.015,
  "note": "Moderate activity, strong signals"
}

{
  "name": "31 - SSF",
  "volume_sensitivity": 0.015,
  "note": "South San Francisco, good signal"
}
```

### Default Value

For new channels, start with **0.01** as a balanced default.

## Tuning Process

### Step 1: Initial Setup
1. Set `volume_sensitivity` to 0.01
2. Enable channel recording
3. Monitor for 30-60 minutes

### Step 2: Analyze Results

Check for these issues:

**Too Many Recordings (False Positives)**
- Symptoms: Many short files, background noise recordings
- Solution: Increase sensitivity (0.015-0.02)

**Missing Transmissions (False Negatives)** 
- Symptoms: Known transmissions not recorded
- Solution: Decrease sensitivity (0.005-0.008)

**Good Balance**
- Symptoms: Transmissions captured reliably, minimal noise
- Solution: Keep current setting

### Step 3: Fine-Tuning

Use log analysis to refine settings:

1. Enable debug logging
2. Monitor RMS values in logs
3. Adjust threshold based on actual RMS ranges

Example log analysis:
```
INFO - Channel: San Mateo, RMS: 0.0034 < 0.005 - SILENT (noise)
INFO - Channel: San Mateo, RMS: 0.0087 > 0.005 - ACTIVE (transmission)  
INFO - Channel: San Mateo, RMS: 0.0156 > 0.005 - ACTIVE (strong signal)
```

## Testing Tools

### Manual Testing

1. **Live Monitoring**: Watch logs during known active periods
2. **Web Interface**: Use real-time status to see detection
3. **File Review**: Check recorded files for quality

### Debug Mode

Enable verbose logging to see RMS values:

```python
# In audio_recorder.py
logging.getLogger().setLevel(logging.DEBUG)
```

### Channel Health Check

Run test script to validate settings:

```bash
cd dev/
python test_channels.py --channel "San Mateo" --duration 300
```

## Troubleshooting

### Common Issues

**No Recordings Generated**
- Check: `volume_sensitivity` too high (try 0.005)
- Check: Stream URL working
- Check: Channel enabled in config

**Too Many Short Files**
- Check: `volume_sensitivity` too low (try 0.015)
- Check: Background noise on stream
- Check: Minimum length filtering working

**Clipped Transmissions**
- Check: `volume_sensitivity` causing late start
- Check: Maximum transmission length (30s default)
- Check: Stream quality and buffering

### Log Analysis

Key log patterns to watch:

```bash
# Good detection
grep "ACTIVE" recording.log | head -10

# Threshold analysis  
grep "RMS" recording.log | awk '{print $NF}' | sort -n

# Channel-specific issues
grep "San Mateo" recording.log | grep "RMS"
```

## Advanced Configuration

### Per-Channel Optimization

For channels with varying signal strength:

1. **Monitor signal patterns** over 24 hours
2. **Identify peak/quiet periods** 
3. **Set threshold** for reliable detection during quiet periods
4. **Validate** no false positives during peak periods

### Batch Optimization

To optimize multiple channels:

1. **Set all to default** (0.01)
2. **Run for 24 hours**
3. **Analyze results** by channel
4. **Adjust in groups** (high/medium/low activity)
5. **Re-test and validate**

## Best Practices

### Initial Deployment
- Start conservative (higher thresholds)
- Monitor closely for first week
- Adjust based on actual usage patterns

### Ongoing Maintenance
- Review monthly for false positives/negatives
- Adjust for seasonal changes (storm season, etc.)
- Document changes and rationale

### Performance Considerations
- Lower thresholds = more CPU usage
- Balance sensitivity with resource usage
- Monitor disk space with sensitive settings

---

*For technical details about the RMS calculation and algorithm, see [SIMPLIFICATION_SUMMARY.md](../SIMPLIFICATION_SUMMARY.md)*
