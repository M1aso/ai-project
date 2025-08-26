# Content Worker Service

## Overview
The Content Worker Service is a Python/Celery-based background processing service that handles video transcoding and media processing tasks for the content management system.

## Features
- 🎥 **Video Transcoding** - Convert videos to multiple formats and resolutions using FFmpeg
- 🔄 **Background Processing** - Asynchronous task processing with Celery
- 📊 **Multiple Presets** - Configurable encoding presets for different quality levels
- 🔗 **Content Service Integration** - Authenticated API calls to update asset status
- 📈 **Prometheus Metrics** - Built-in monitoring and retry tracking
- ⚡ **Retry Logic** - Automatic retry with exponential backoff on failures

## Technology Stack
- **Language**: Python 3.12
- **Task Queue**: Celery with RabbitMQ broker
- **Result Backend**: Redis
- **Video Processing**: FFmpeg
- **HTTP Client**: Requests for API communication
- **Monitoring**: Prometheus client for metrics
- **Configuration**: YAML-based preset configuration

## Architecture
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   RabbitMQ      │    │   Content    │    │   Content       │
│   (Broker)      │◄──►│   Worker     │◄──►│   Service       │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │    Redis     │
                       │  (Results)   │
                       └──────────────┘
```

## Task Processing

### Video Transcoding Task
```python
def transcode_video(
    asset_id: str,
    source_path: str, 
    preset: str,
    max_retries: int = 3
):
    # 1. Validate preset exists
    # 2. Run FFmpeg with preset configuration
    # 3. Update Content Service with result
    # 4. Handle retries on failure
```

### Transcoding Presets
Configured in `app/presets.yaml`:
```yaml
720p:
  ffmpeg_args:
    - "-c:v"
    - "libx264"
    - "-preset"
    - "medium"
    - "-crf"
    - "23"
    - "-s"
    - "1280x720"
    - "-c:a"
    - "aac"
    - "-b:a"
    - "128k"

1080p:
  ffmpeg_args:
    - "-c:v"
    - "libx264"
    - "-preset"
    - "medium"
    - "-crf"
    - "21"
    - "-s"
    - "1920x1080"
    - "-c:a"
    - "aac"
    - "-b:a"
    - "192k"
```

## Environment Variables
```bash
# Message Queue
RABBITMQ_URL=amqp://user:pass@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Content Service Integration
CONTENT_API_URL=http://api.example.com
CONTENT_WORKER_API_KEY=service-api-key-for-auth

# File Storage
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio-access-key
MINIO_SECRET_KEY=minio-secret-key
MINIO_SECURE=false

# Database (for metadata)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Logging
LOG_LEVEL=DEBUG
```

## Content Service Integration

### Authentication
The worker authenticates with the Content Service using a service API key:
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
```

### Asset Status Updates
```python
# Update asset status after successful transcoding
def update_asset(asset_id: str, data: dict):
    url = f"{content_api_url}/api/content/media-assets/{asset_id}"
    response = requests.patch(url, json=data, headers=headers)
    response.raise_for_status()
```

### Status Flow
1. **pending** - Initial status when asset is created
2. **processing** - Worker starts transcoding
3. **ready** - Transcoding completed successfully
4. **failed** - Transcoding failed after all retries

## Queue Configuration
```python
# Celery configuration
CELERY_TASK_QUEUES = (
    Queue("content-transcode", durable=True),
)
CELERY_TASK_DEFAULT_QUEUE = "content-transcode"
```

## Monitoring & Metrics

### Prometheus Metrics
- `transcode_retries_total` - Counter of transcode retry attempts by preset
- Task execution time and success/failure rates (via Celery)

### Health Monitoring
- **Queue Health**: Monitor RabbitMQ connection
- **Redis Health**: Monitor result backend connection
- **Task Processing**: Track task completion rates
- **FFmpeg Status**: Monitor transcoding success rates

## Development

### Prerequisites
- Python 3.12+
- FFmpeg installed
- RabbitMQ server
- Redis server
- Access to Content Service API

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start Celery worker
celery -A app.worker.celery_app worker -Q content-transcode --loglevel=info

# Monitor tasks (in another terminal)
celery -A app.worker.celery_app flower
```

### Testing
```bash
# Run unit tests
pytest

# Test with mock Content API
pytest tests/test_transcode.py -v

# Test FFmpeg integration
pytest tests/test_ffmpeg.py -v
```

## Task Examples

### Queue a Transcoding Task
```python
from app.tasks.transcode import transcode_video

# Queue video transcoding task
result = transcode_video.delay(
    asset_id="asset-123",
    source_path="/tmp/video.mp4", 
    preset="720p"
)

# Check task status
print(result.status)  # PENDING, SUCCESS, FAILURE
print(result.result)  # Task result or error message
```

### Custom Preset Configuration
```yaml
# Add to app/presets.yaml
mobile:
  ffmpeg_args:
    - "-c:v"
    - "libx264"
    - "-preset"
    - "fast"
    - "-crf"
    - "28"
    - "-s"
    - "640x360"
    - "-c:a"
    - "aac"
    - "-b:a"
    - "64k"
    - "-movflags"
    - "+faststart"
```

## Error Handling

### Retry Logic
- **Exponential Backoff**: 2^attempt seconds between retries
- **Max Retries**: Configurable (default: 3)
- **Failure Notification**: Updates Content Service with error details

### Common Errors
1. **FFmpeg Errors**: Invalid codec, corrupted file, insufficient disk space
2. **API Errors**: Content Service unavailable, authentication failure
3. **File Errors**: Source file not found, permission denied

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Python 3.12 slim with FFmpeg
- **Scaling**: Horizontal pod autoscaling based on queue length
- **Health Checks**: Celery worker health monitoring
- **Resource Limits**: CPU and memory limits for transcoding tasks

## Security Features
- 🔑 **Service Authentication** - API key-based auth with Content Service
- 🔒 **Secure Connections** - TLS for external API calls
- 📁 **File Validation** - Input validation for file paths and presets
- 🛡️ **Process Isolation** - Containerized execution environment
- 📊 **Audit Logging** - Comprehensive task execution logging

## Performance Tuning

### Concurrency
```bash
# Adjust worker concurrency based on CPU cores
celery -A app.worker.celery_app worker --concurrency=4

# Use prefork pool for CPU-intensive tasks
celery -A app.worker.celery_app worker --pool=prefork
```

### Resource Management
- **Memory**: Monitor FFmpeg memory usage during transcoding
- **CPU**: Balance transcoding quality vs. processing time
- **Disk**: Cleanup temporary files after processing
- **Network**: Optimize file transfer for large video files

## Documentation
- **Task Monitoring**: Use Celery Flower for task monitoring
- **Queue Management**: RabbitMQ management interface
- **Metrics**: Prometheus metrics for operational monitoring
