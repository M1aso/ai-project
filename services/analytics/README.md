# Analytics Service

## Overview
The Analytics Service is a Python/FastAPI-based service that collects, processes, and reports on user behavior and system metrics across the AI Project platform.

## Features
- 📊 **Event Ingestion** - Collect user behavior events in real-time
- 📈 **Metrics Calculation** - Daily active users, engagement metrics
- 📋 **Data Export** - Export analytics data in CSV and Excel formats
- 🔒 **JWT Authentication** - Secure API access with token validation
- 📦 **Batch Processing** - Efficient bulk event ingestion
- 🎯 **Event Filtering** - Configurable event type filtering and validation

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT token validation
- **Data Export**: CSV and Excel (openpyxl) support
- **Task Processing**: Celery for background processing
- **Database Migrations**: Alembic

## API Endpoints

### Protected Endpoints (JWT Required)
- `POST /api/analytics/ingest` - Ingest user behavior events
- `GET /api/analytics/reports/dau` - Get daily active users count
- `GET /api/analytics/reports/events` - Export events data (CSV/Excel)

### Public Endpoints
- `GET /api/analytics/healthz` - Health check

## Event Ingestion

### Event Schema
```json
{
  "ts": "2024-01-01T12:00:00Z",
  "user_id": "user-123",
  "type": "page_view",
  "src": "web_app",
  "payload": {
    "page": "/dashboard",
    "referrer": "/login",
    "session_id": "sess-456"
  }
}
```

### Supported Event Types
- `page_view` - Page navigation events
- `button_click` - User interaction events
- `form_submit` - Form submission events
- `video_play` - Media consumption events
- `course_complete` - Learning progress events
- `search_query` - Search behavior events
- `error_occurred` - Error tracking events

### Batch Ingestion
```bash
curl -X POST "http://api.example.com/api/analytics/ingest" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "ts": "2024-01-01T12:00:00Z",
      "user_id": "user-123",
      "type": "page_view",
      "src": "web_app",
      "payload": {"page": "/dashboard"}
    },
    {
      "ts": "2024-01-01T12:01:00Z", 
      "user_id": "user-123",
      "type": "button_click",
      "src": "web_app",
      "payload": {"button_id": "save_profile"}
    }
  ]'
```

## Reports & Analytics

### Daily Active Users (DAU)
```bash
curl -X GET "http://api.example.com/api/analytics/reports/dau" \
  -H "Authorization: Bearer <jwt-token>"

# Response
{
  "dau": 1247,
  "date": "2024-01-01",
  "period": "24h"
}
```

### Data Export
```bash
# Export as CSV
curl -X GET "http://api.example.com/api/analytics/reports/events?format=csv" \
  -H "Authorization: Bearer <jwt-token>" \
  -o events.csv

# Export as Excel
curl -X GET "http://api.example.com/api/analytics/reports/events?format=xlsx" \
  -H "Authorization: Bearer <jwt-token>" \
  -o events.xlsx
```

## Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key

# Task Queue (for background processing)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Rate Limiting
MAX_BATCH_SIZE=1000
RATE_LIMIT_PER_MINUTE=100

# Data Retention
EVENT_RETENTION_DAYS=90
METRICS_RETENTION_DAYS=365

# Logging
LOG_LEVEL=DEBUG
```

## Database Schema

### Events Table
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP WITH TIME ZONE NOT NULL,
    user_id VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    src VARCHAR,
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_events_ts ON events(ts);
CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_created_at ON events(created_at);
```

### Metrics Table
```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    metric_name VARCHAR NOT NULL,
    metric_value INTEGER NOT NULL,
    dimensions JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Unique constraint for daily metrics
CREATE UNIQUE INDEX idx_metrics_date_name ON metrics(date, metric_name);
```

## Event Processing Pipeline

### 1. Ingestion
```python
@router.post("/ingest")
def ingest_events(
    events: List[EventIn],
    db: Session = Depends(get_db),
    current_user: Dict = Depends(get_current_user)
):
    # Validate batch size
    if len(events) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=413, detail="batch too large")
    
    # Store events in database
    db_events = [Event(**event.dict()) for event in events]
    db.add_all(db_events)
    db.commit()
    
    return {"ingested": len(events)}
```

### 2. Metrics Calculation
```python
def calculate_daily_metrics():
    """Background task to calculate daily metrics"""
    today = datetime.now().date()
    
    # Calculate DAU
    dau = db.query(Event.user_id)\
            .filter(Event.ts >= today)\
            .distinct()\
            .count()
    
    # Store metric
    metric = Metric(
        date=today,
        metric_name="dau",
        metric_value=dau
    )
    db.add(metric)
    db.commit()
```

## Client Integration

### JavaScript SDK
```javascript
class AnalyticsClient {
  constructor(apiUrl, token) {
    this.apiUrl = apiUrl;
    this.token = token;
    this.eventQueue = [];
  }

  track(eventType, payload = {}, userId = null) {
    const event = {
      ts: new Date().toISOString(),
      user_id: userId || this.getCurrentUserId(),
      type: eventType,
      src: 'web_app',
      payload
    };
    
    this.eventQueue.push(event);
    
    // Auto-flush when queue reaches threshold
    if (this.eventQueue.length >= 10) {
      this.flush();
    }
  }

  async flush() {
    if (this.eventQueue.length === 0) return;
    
    const events = [...this.eventQueue];
    this.eventQueue = [];
    
    try {
      await fetch(`${this.apiUrl}/api/analytics/ingest`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(events)
      });
    } catch (error) {
      console.error('Failed to send analytics events:', error);
      // Re-queue events for retry
      this.eventQueue.unshift(...events);
    }
  }
}

// Usage
const analytics = new AnalyticsClient('http://api.example.com', 'jwt-token');

// Track page views
analytics.track('page_view', { page: '/dashboard' });

// Track user interactions
analytics.track('button_click', { button_id: 'save_profile' });

// Track custom events
analytics.track('course_complete', { 
  course_id: 'course-123',
  completion_time: 3600,
  score: 85
});
```

### React Hook
```typescript
import { useEffect, useRef } from 'react';

export function useAnalytics(apiUrl: string, token: string) {
  const analytics = useRef(new AnalyticsClient(apiUrl, token));

  useEffect(() => {
    // Auto-flush events before page unload
    const handleBeforeUnload = () => {
      analytics.current.flush();
    };
    
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  const track = (eventType: string, payload: any = {}) => {
    analytics.current.track(eventType, payload);
  };

  return { track };
}
```

## Data Privacy & Compliance

### Data Anonymization
```python
def anonymize_user_data(user_id: str) -> str:
    """Hash user IDs for privacy protection"""
    import hashlib
    return hashlib.sha256(user_id.encode()).hexdigest()[:16]
```

### Data Retention
```python
def cleanup_old_events():
    """Remove events older than retention period"""
    cutoff_date = datetime.now() - timedelta(days=EVENT_RETENTION_DAYS)
    
    deleted_count = db.query(Event)\
                     .filter(Event.created_at < cutoff_date)\
                     .delete()
    
    db.commit()
    return deleted_count
```

## Development

### Prerequisites
- Python 3.12+
- PostgreSQL database
- Redis (for Celery tasks)

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (for background tasks)
celery -A app.worker worker --loglevel=info

# Run tests
pytest
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Test event ingestion
pytest tests/test_ingest.py -v

# Test report generation
pytest tests/test_reports.py -v
```

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Built from Python 3.12 slim
- **Health Checks**: `/healthz` endpoint
- **Database Migrations**: Automatic via init container
- **Background Tasks**: Separate Celery worker deployment
- **Monitoring**: Prometheus metrics and structured logging

## Security Features
- 🔒 **JWT Authentication** - All endpoints require valid tokens
- 📊 **Rate Limiting** - Protection against event spam
- 🛡️ **Input Validation** - Strict event schema validation
- 🔐 **Data Privacy** - Optional user ID anonymization
- 📝 **Audit Logging** - Complete event ingestion audit trail
- 🗑️ **Data Retention** - Automatic cleanup of old events

## Performance Optimization

### Database Indexing
```sql
-- Optimize common queries
CREATE INDEX idx_events_user_ts ON events(user_id, ts);
CREATE INDEX idx_events_type_ts ON events(type, ts);

-- Partial indexes for active data
CREATE INDEX idx_events_recent ON events(ts) 
WHERE ts > NOW() - INTERVAL '30 days';
```

### Batch Processing
- **Event Batching**: Process events in batches of 1000
- **Connection Pooling**: Efficient database connections
- **Background Tasks**: Async metrics calculation
- **Caching**: Redis caching for frequently accessed metrics

## Monitoring & Alerting

### Key Metrics
- **Event Ingestion Rate**: Events per second
- **Processing Latency**: Time from ingestion to storage
- **Error Rate**: Failed event processing percentage
- **Database Performance**: Query execution times
- **Queue Length**: Celery task queue backlog

### Alerts
- High error rate in event ingestion
- Database connection failures
- Celery worker failures
- Disk space warnings for event storage

## Documentation
- **OpenAPI Spec**: `/api/analytics/openapi.json`
- **Swagger UI**: `/api/analytics/docs`
- **Event Schema**: Detailed event type documentation
- **Integration Guide**: Client SDK documentation