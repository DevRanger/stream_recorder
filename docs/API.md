# API Documentation

## Overview

The Radio Stream Recorder provides a RESTful API for managing channels, recordings, and system operations.

Base URL: `http://localhost:8000`

## Authentication

Currently, no authentication is required. The API is designed for local network use.

## Endpoints

### Channels

#### GET /api/channels
Returns a list of all configured radio channels.

**Response:**
```json
{
  "Channel_Name": {
    "name": "Friendly Channel Name",
    "stream_url": "http://stream.url/path",
    "silence_threshold": -50,
    "silence_gap": 2.0,
    "status": "active|inactive|error"
  }
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

### Recordings

#### GET /api/recordings/channel/{channel_name}
Returns recordings for a specific channel.

**Parameters:**
- `channel_name` (path): Channel identifier
- `limit` (query): Maximum number of recordings (default: 50)
- `start_date` (query): Start date filter (YYYY-MM-DD or YYYY-MM-DDTHH:MM)
- `end_date` (query): End date filter (YYYY-MM-DD or YYYY-MM-DDTHH:MM)

**Example:**
```
GET /api/recordings/channel/2_-_Sheriff?limit=100&start_date=2025-08-20&end_date=2025-08-27
```

**Response:**
```json
[
  {
    "filename": "20250826_140500_123_2_-_Sheriff.mp3",
    "timestamp": "2025-08-26T14:05:00",
    "duration": 5.2,
    "size": 125440,
    "channel": "2_-_Sheriff"
  }
]
```

**Status Codes:**
- 200: Success
- 404: Channel not found
- 500: Server error

---

#### GET /api/recording/{filename}
Download or stream a specific recording file.

**Parameters:**
- `filename` (path): Recording filename

**Response:**
- Audio file stream (MP3)
- Supports range requests for partial content

**Status Codes:**
- 200: Success (full file)
- 206: Partial content (range request)
- 404: File not found
- 500: Server error

---

### System Status

#### GET /api/status
Returns current system status and statistics.

**Response:**
```json
{
  "status": "running",
  "uptime": 3600,
  "active_channels": 25,
  "total_recordings": 1250,
  "disk_usage": {
    "total": "100GB",
    "used": "45GB",
    "free": "55GB"
  },
  "memory_usage": {
    "total": "8GB",
    "used": "2.1GB",
    "available": "5.9GB"
  }
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

### Cleanup Operations

#### POST /api/cleanup-temp
Manually trigger temporary file cleanup.

**Response:**
```json
{
  "status": "success",
  "message": "Cleanup completed",
  "files_removed": {
    "age_based": 15,
    "orphaned": 3,
    "total": 18
  }
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

#### GET /api/cleanup-status
Get temporary file cleanup statistics.

**Response:**
```json
{
  "temp_files": {
    "total": 45,
    "by_age": {
      "under_1_hour": 30,
      "1_to_24_hours": 10,
      "over_24_hours": 5
    },
    "by_channel": {
      "2_-_Sheriff": 12,
      "25_-_San_Mateo": 8,
      "other": 25
    }
  },
  "last_cleanup": "2025-08-26T18:00:00",
  "next_cleanup": "2025-08-26T19:00:00"
}
```

**Status Codes:**
- 200: Success
- 500: Server error

---

## Response Format

All API responses use JSON format with consistent structure:

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. The API is designed for local use.

## Examples

### Get All Channels
```bash
curl http://localhost:8000/api/channels
```

### Get Recent Recordings for Sheriff Channel
```bash
curl "http://localhost:8000/api/recordings/channel/2_-_Sheriff?limit=10"
```

### Download a Recording
```bash
curl -O "http://localhost:8000/api/recording/20250826_140500_123_2_-_Sheriff.mp3"
```

### Check System Status
```bash
curl http://localhost:8000/api/status
```

### Trigger Manual Cleanup
```bash
curl -X POST http://localhost:8000/api/cleanup-temp
```

## WebSocket Events (Future)

Currently not implemented, but planned for real-time updates:
- Channel status changes
- New recording notifications
- System alerts

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 206: Partial Content (range requests)
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error

Detailed error messages are provided in the JSON response body.

## CORS

CORS is enabled for local development. For production use, configure appropriate CORS policies.

## Content Types

- Request: `application/json` for POST/PUT requests
- Response: `application/json` for API endpoints
- Audio files: 
  - `audio/flac` for FLAC recordings
  - `audio/mpeg` for MP3 recordings
