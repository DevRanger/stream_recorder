# Architecture Documentation

## System Overview

The Radio Stream Recorder is a multi-threaded Python application that simultaneously records audio transmissions from multiple radio channels. It uses a Flask web framework for the user interface and API, with a custom audio processing engine for stream management.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │────│  Flask Web App  │────│ Audio Recorder  │
│                 │    │                 │    │     Engine      │
│ • Channel View  │    │ • REST API      │    │ • Multi-stream  │
│ • Recording UI  │    │ • File Serving  │    │ • Detection     │
│ • Batch Play    │    │ • Status Info   │    │ • Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Configuration  │    │  File System    │
                       │                 │    │                 │
                       │ • Channels      │    │ • Audio Files   │
                       │ • Settings      │    │ • Metadata      │
                       │ • Thresholds    │    │ • Temp Files    │
                       └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Flask Web Application (`main.py`)

**Purpose**: Provides web interface and REST API for system interaction.

**Key Features**:
- REST API endpoints for channels, recordings, and system status
- Static file serving for audio recordings
- Web interface with real-time updates
- CORS support for cross-origin requests

**Threading Model**:
- Main thread handles HTTP requests
- Separate thread pool for file operations
- Non-blocking audio file serving with range request support

**API Endpoints**:
```python
/api/channels          # GET - List all channels
/api/recordings/       # GET - Channel recordings with filtering
/api/recording/        # GET - Download specific recording
/api/status           # GET - System status and statistics
/api/cleanup-temp     # POST - Manual cleanup trigger
/api/cleanup-status   # GET - Cleanup statistics
```

### 2. Audio Recording Engine (`audio_recorder.py`)

**Purpose**: Core engine that manages audio streams and recording logic.

**Architecture**:
```
AudioRecorder (Main Class)
├── Channel Management
│   ├── Stream Connection
│   ├── Audio Buffering
│   └── Error Handling
├── Transmission Detection
│   ├── Silence Analysis
│   ├── Audio Level Monitoring
│   └── Transmission Validation
├── Audio Processing
│   ├── FFmpeg Integration
│   ├── Format Conversion
│   └── Quality Preservation
└── File Management
    ├── Temporary Files
    ├── Final Recordings
    └── Cleanup Operations
```

**Threading Model**:
- One thread per radio channel
- Background cleanup scheduler thread
- Thread-safe operations with locks
- Graceful shutdown handling

**Key Classes and Methods**:
```python
class AudioRecorder:
    def __init__(self, channels_config)
    def start_recording(self, channel_name)
    def stop_recording(self, channel_name)
    def process_audio_stream(self, channel_name)
    def detect_transmission(self, audio_data, threshold)
    def save_transmission_ffmpeg(self, channel_name, start_time, end_time)
    def cleanup_temp_files(self, max_age_hours=1)
```

### 3. Audio Processing Pipeline

**Stream Processing Flow**:
```
Radio Stream → Audio Buffer → Transmission Detection → Recording Decision
                     ↓
                Audio Analysis
             ┌─────────────────┐
             │ • Silence Level │
             │ • Duration      │
             │ • Quality Check │
             └─────────────────┘
                     ↓
              Recording Trigger
             ┌─────────────────┐
             │ • Start Capture │
             │ • Monitor End   │
             │ • Validate      │
             └─────────────────┘
                     ↓
              File Processing
             ┌─────────────────┐
             │ • FFmpeg Extract│
             │ • Metadata Gen  │
             │ • Cleanup Temp  │
             └─────────────────┘
```

**Transmission Detection Algorithm**:
1. **Continuous Monitoring**: Analyze audio in real-time chunks
2. **Silence Detection**: Compare audio levels to threshold
3. **Transmission Start**: Audio above threshold triggers recording
4. **Transmission End**: Sustained silence below threshold ends recording
5. **Validation**: Check minimum/maximum duration requirements
6. **Processing**: Extract final audio using FFmpeg
7. **Cleanup**: Remove temporary files

### 4. Configuration Management

**Configuration Hierarchy**:
```
System Defaults (audio_recorder.py)
         ↓
Global Settings (config.py)
         ↓
Channel Configuration (radio_channels.json)
         ↓
Runtime Parameters (API/UI)
```

**Configuration Loading**:
```python
def load_configuration():
    # 1. Load system defaults
    defaults = get_system_defaults()
    
    # 2. Load channel configuration
    channels = load_channels_config()
    
    # 3. Apply channel-specific overrides
    for channel in channels:
        apply_channel_settings(channel, defaults)
    
    # 4. Validate configuration
    validate_settings(channels)
    
    return channels
```

## Data Flow

### 1. Audio Stream Processing

```
Internet Stream → HTTP Client → Audio Buffer → PyDub Analysis → Decision Engine
                                      ↓
                              Temporary File Storage
                                      ↓
                              FFmpeg Processing → Final MP3 → Metadata JSON
```

### 2. Web Interface Data Flow

```
Browser Request → Flask Router → API Handler → Data Processing → JSON Response
                                     ↓
                              File System Access
                                     ↓
                              Audio File Stream → HTTP Response → Browser
```

### 3. File Management Flow

```
Temp Files → Age Check → Orphan Check → Removal Decision → File Deletion
     ↓              ↓            ↓              ↓              ↓
   Created      1hr+ old    No Final File   Remove?      Cleanup Log
```

## Concurrency Model

### Thread Management

**Main Application Threads**:
1. **Flask Main Thread**: Handles HTTP requests and web interface
2. **Channel Threads**: One per radio channel (25+ threads)
3. **Cleanup Thread**: Background maintenance operations
4. **File Serving Threads**: Concurrent audio file downloads

**Thread Safety**:
- Shared data protected with threading locks
- Thread-local storage for channel-specific data
- Atomic file operations for recording safety
- Graceful shutdown coordination

**Resource Management**:
```python
class ThreadSafeAudioRecorder:
    def __init__(self):
        self._lock = threading.Lock()
        self._channel_threads = {}
        self._shutdown_event = threading.Event()
    
    def start_channel(self, channel_name):
        with self._lock:
            if channel_name not in self._channel_threads:
                thread = threading.Thread(
                    target=self._process_channel,
                    args=(channel_name,),
                    daemon=True
                )
                self._channel_threads[channel_name] = thread
                thread.start()
```

## Storage Architecture

### File Organization

```
audio_files/
├── Channel_Name_1/
│   ├── YYYYMMDD_HHMMSS_mmm_Channel_Name_1.mp3
│   ├── YYYYMMDD_HHMMSS_mmm_Channel_Name_1_metadata.json
│   └── temp_YYYYMMDD_HHMMSS_mmm_Channel_Name_1.mp3
├── Channel_Name_2/
│   └── ...
└── logs/
    ├── recording.log
    └── cleanup.log
```

### File Naming Convention

**Recording Files**:
- Format: `YYYYMMDD_HHMMSS_mmm_ChannelName.mp3`
- Example: `20250826_143022_456_2_-_Sheriff.mp3`
- Timestamp includes milliseconds for uniqueness

**Metadata Files**:
- Format: `YYYYMMDD_HHMMSS_mmm_ChannelName_metadata.json`
- Contains: duration, file size, channel info, timestamps

**Temporary Files**:
- Format: `temp_YYYYMMDD_HHMMSS_mmm_ChannelName.mp3`
- Used during recording and processing
- Automatically cleaned up after use

### Storage Management

**Cleanup Strategy**:
1. **Immediate**: Remove temp files after processing
2. **Hourly**: Background cleanup of orphaned temp files
3. **Daily**: Remove recordings older than retention period
4. **On-demand**: Manual cleanup via API

## Error Handling and Resilience

### Error Categories

1. **Network Errors**: Stream disconnection, timeout, unreachable
2. **Audio Processing Errors**: Corrupt audio, format issues, FFmpeg failures
3. **File System Errors**: Disk full, permission denied, I/O errors
4. **Configuration Errors**: Invalid settings, missing files, malformed JSON

### Recovery Mechanisms

**Stream Reconnection**:
```python
def robust_stream_connection(self, channel_name, max_retries=5):
    for attempt in range(max_retries):
        try:
            return self.connect_stream(channel_name)
        except Exception as e:
            self.log_error(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

**File Operation Safety**:
```python
def safe_file_operation(self, operation, filepath, max_retries=3):
    for attempt in range(max_retries):
        try:
            return operation(filepath)
        except IOError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
                continue
            else:
                self.log_error(f"File operation failed: {e}")
                raise
```

### Monitoring and Logging

**Log Levels**:
- **DEBUG**: Detailed processing information
- **INFO**: Normal operations, recordings, cleanup
- **WARNING**: Recoverable errors, retries
- **ERROR**: Serious errors, failed operations
- **CRITICAL**: System failures, shutdown events

**Health Monitoring**:
- Channel connection status
- Recording success rates
- Disk space utilization
- Memory and CPU usage
- Error frequency tracking

## Performance Characteristics

### Resource Usage

**Memory**:
- Base application: ~50MB
- Per channel: ~5-10MB (audio buffers)
- Total for 25 channels: ~300-400MB

**CPU**:
- Light load during silence
- Higher load during transmission processing
- FFmpeg processing spikes
- Generally <10% on modern hardware

**Storage**:
- ~1MB per minute of recorded audio
- Metadata files: ~1KB each
- Temporary files: cleaned automatically

### Scalability Considerations

**Horizontal Scaling**:
- Multiple application instances
- Load balancing across instances
- Shared storage for recordings

**Vertical Scaling**:
- More CPU cores for parallel processing
- Additional memory for more channels
- Faster storage for improved I/O

### Optimization Strategies

1. **Audio Processing**:
   - Efficient chunk size selection
   - Minimal audio format conversions
   - FFmpeg stream copy for quality preservation

2. **File I/O**:
   - Asynchronous file operations
   - Batch cleanup operations
   - Strategic temporary file placement

3. **Network**:
   - Connection pooling
   - Retry with exponential backoff
   - Stream buffering optimization

## Security Considerations

### Network Security
- No authentication currently implemented
- Designed for trusted network environments
- Consider VPN or firewall restrictions

### File System Security
- Run with minimal necessary permissions
- Secure audio file storage
- Regular backup of recordings and configuration

### Data Privacy
- Audio recordings may contain sensitive information
- Consider encryption for storage
- Implement retention policies

## Future Architecture Enhancements

### Planned Improvements
1. **Database Integration**: Store metadata in database for better querying
2. **Real-time WebSocket**: Live updates for web interface
3. **Authentication System**: User management and access control
4. **Distributed Architecture**: Multi-node deployment capability
5. **Advanced Analytics**: Recording statistics and trends
6. **Plugin System**: Extensible audio processing pipeline
