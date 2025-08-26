# Notifications Service

## Overview
The Notifications Service is a Python/FastAPI-based multi-channel notification service that handles email, SMS, push notifications, and real-time notifications across the AI Project platform.

## Features
- 📧 **Email Notifications** - Welcome emails, alerts, newsletters with HTML templates
- 📱 **Push Notifications** - Mobile and web push messages
- 📲 **SMS Notifications** - Text message alerts and verification codes
- 🔔 **Real-time Notifications** - Instant notification delivery via WebSocket
- 🎨 **Template Engine** - Jinja2-based templating system with MJML support
- 🔒 **JWT Authentication** - Secure API access with token validation
- ⚡ **Background Processing** - Asynchronous notification delivery with Celery
- 🔄 **Retry Logic** - Automatic retry with exponential backoff on failures

## Technology Stack
- **Framework**: FastAPI (Python)
- **Template Engine**: Jinja2 with MJML for email templates
- **Task Queue**: Celery with RabbitMQ broker
- **Authentication**: JWT token validation
- **Email**: SMTP integration (Gmail, SendGrid, etc.)
- **SMS**: Integration with SMS providers (Twilio, etc.)
- **Push**: Web Push API and mobile push notifications

## API Endpoints

### Protected Endpoints (JWT Required)
- `POST /api/notify/send` - Send notification (queued for background processing)
- `POST /api/notify/preview` - Preview notification template without sending

### Public Endpoints
- `GET /healthz` - Health check
- `GET /api/notifications/openapi.json` - OpenAPI specification
- `GET /api/notifications/docs` - Swagger UI documentation

## Notification Channels

### Email Notifications
```json
{
  "channel": "email",
  "recipient": "user@example.com",
  "template": "welcome",
  "data": {
    "name": "John Doe",
    "verification_url": "https://app.example.com/verify?token=abc123"
  }
}
```

### SMS Notifications
```json
{
  "channel": "sms",
  "recipient": "+1234567890",
  "template": "verification_code",
  "data": {
    "code": "123456",
    "expires_in": "10 minutes"
  }
}
```

### Push Notifications
```json
{
  "channel": "push",
  "recipient": "user-123",
  "template": "new_message",
  "data": {
    "title": "New Message",
    "body": "You have a new message from John",
    "icon": "/icons/message.png",
    "url": "/chat/room-123"
  }
}
```

## Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Authentication
JWT_SECRET_KEY=your-jwt-secret-key

# Task Queue
REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://user:pass@rabbitmq:5672//

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourapp.com
FROM_NAME=Your App Name

# SMS Configuration (Twilio example)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Push Notifications
VAPID_PUBLIC_KEY=your-vapid-public-key
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_EMAIL=mailto:admin@yourapp.com

# Rate Limiting
MAX_NOTIFICATIONS_PER_MINUTE=60
MAX_NOTIFICATIONS_PER_HOUR=1000

# Logging
LOG_LEVEL=DEBUG
```

## Template System

### Template Structure
```
app/templates/
├── email/
│   ├── welcome.mjml          # Welcome email template
│   ├── password_reset.mjml   # Password reset email
│   └── notification.mjml     # General notification email
├── sms/
│   ├── verification_code.txt # SMS verification template
│   └── alert.txt            # SMS alert template
└── push/
    ├── new_message.json     # Push notification template
    └── system_alert.json   # System alert push template
```

### Email Template (MJML)
```xml
<!-- app/templates/email/welcome.mjml -->
<mjml>
  <mj-head>
    <mj-title>Welcome to {{ app_name }}</mj-title>
  </mj-head>
  <mj-body>
    <mj-section>
      <mj-column>
        <mj-text>
          <h1>Welcome, {{ name }}!</h1>
          <p>Thank you for joining {{ app_name }}. To get started, please verify your email address.</p>
          <a href="{{ verification_url }}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
            Verify Email
          </a>
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
```

### SMS Template
```
<!-- app/templates/sms/verification_code.txt -->
Your {{ app_name }} verification code is: {{ code }}

This code expires in {{ expires_in }}.
```

### Push Template
```json
{
  "title": "{{ title }}",
  "body": "{{ body }}",
  "icon": "{{ icon | default('/icons/default.png') }}",
  "badge": "{{ badge | default('/icons/badge.png') }}",
  "data": {
    "url": "{{ url }}",
    "timestamp": "{{ timestamp }}"
  }
}
```

## API Usage

### Send Notification
```bash
curl -X POST "http://api.example.com/api/notify/send" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "template": "welcome",
    "data": {
      "name": "John Doe",
      "app_name": "AI Project",
      "verification_url": "https://app.example.com/verify?token=abc123"
    },
    "idempotency_key": "welcome-user-123-2024-01-01"
  }'

# Response
{
  "status": "queued",
  "user_id": "user-123",
  "notification_id": "notif-456"
}
```

### Preview Notification
```bash
curl -X POST "http://api.example.com/api/notify/preview" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "template": "welcome", 
    "data": {
      "name": "John Doe",
      "app_name": "AI Project"
    }
  }'

# Response
{
  "rendered_content": "<html>...</html>",
  "subject": "Welcome to AI Project",
  "preview_url": "https://api.example.com/preview/notif-789"
}
```

## Background Processing

### Celery Tasks
```python
@celery_app.task(bind=True, max_retries=3)
def send_notification_task(self, notification_data):
    try:
        # Process notification based on channel
        if notification_data['channel'] == 'email':
            send_email(notification_data)
        elif notification_data['channel'] == 'sms':
            send_sms(notification_data)
        elif notification_data['channel'] == 'push':
            send_push(notification_data)
            
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Queue Configuration
```python
# Celery configuration
CELERY_TASK_QUEUES = (
    Queue("notifications", durable=True),
    Queue("notifications.priority", durable=True),
)

# Route high-priority notifications to priority queue
CELERY_TASK_ROUTES = {
    'send_sms_task': {'queue': 'notifications.priority'},
    'send_email_task': {'queue': 'notifications'},
}
```

## Event-Driven Notifications

### Event Subscribers
```python
# app/subscribers.py
from app.event_bus import EventBus

@EventBus.subscribe('user.registered')
def handle_user_registered(payload):
    """Send welcome email when user registers"""
    send_notification_task.delay({
        'channel': 'email',
        'recipient': payload['email'],
        'template': 'welcome',
        'data': {
            'name': payload['name'],
            'verification_url': payload['verification_url']
        }
    })

@EventBus.subscribe('password.reset.requested')
def handle_password_reset(payload):
    """Send password reset email"""
    send_notification_task.delay({
        'channel': 'email',
        'recipient': payload['email'],
        'template': 'password_reset',
        'data': {
            'reset_url': payload['reset_url'],
            'expires_in': '1 hour'
        }
    })
```

## Client Integration

### JavaScript SDK
```javascript
class NotificationClient {
  constructor(apiUrl, token) {
    this.apiUrl = apiUrl;
    this.token = token;
  }

  async sendNotification(channel, recipient, template, data, idempotencyKey = null) {
    const payload = {
      channel,
      recipient,
      template,
      data,
      ...(idempotencyKey && { idempotency_key: idempotencyKey })
    };

    const response = await fetch(`${this.apiUrl}/api/notify/send`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    return response.json();
  }

  async previewNotification(channel, template, data) {
    const payload = { channel, template, data };

    const response = await fetch(`${this.apiUrl}/api/notify/preview`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    return response.json();
  }
}

// Usage
const notifications = new NotificationClient('http://api.example.com', 'jwt-token');

// Send welcome email
await notifications.sendNotification(
  'email',
  'user@example.com',
  'welcome',
  { name: 'John Doe', app_name: 'AI Project' },
  'welcome-user-123'
);

// Send SMS verification
await notifications.sendNotification(
  'sms',
  '+1234567890',
  'verification_code',
  { code: '123456', expires_in: '10 minutes' }
);
```

## Development

### Prerequisites
- Python 3.12+
- Redis server
- RabbitMQ server
- SMTP server access (Gmail, SendGrid, etc.)

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload --port 8000

# Start Celery worker
celery -A app.worker worker --loglevel=info

# Start Celery beat (for scheduled notifications)
celery -A app.worker beat --loglevel=info

# Monitor tasks
celery -A app.worker flower
```

### Testing
```bash
# Run all tests
pytest

# Test email sending
pytest tests/test_email.py -v

# Test template rendering
pytest tests/test_templates.py -v

# Test with mock providers
pytest --mock-providers
```

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Built from Python 3.12 slim
- **Health Checks**: `/healthz` endpoint
- **Background Workers**: Separate Celery worker deployment
- **Template Storage**: ConfigMaps for email templates
- **Secrets Management**: Kubernetes secrets for API keys
- **Monitoring**: Prometheus metrics and structured logging

## Security Features
- 🔒 **JWT Authentication** - All endpoints require valid tokens
- 🔑 **API Key Management** - Secure storage of third-party API keys
- ⚡ **Rate Limiting** - Protection against notification spam
- 🛡️ **Input Validation** - Strict validation of notification payloads
- 📧 **Email Security** - SPF, DKIM, and DMARC configuration
- 🔐 **Encryption** - TLS encryption for all external communications

## Monitoring & Observability

### Metrics
- **Notification Volume**: Notifications sent per channel
- **Delivery Rate**: Success/failure rates by provider
- **Processing Time**: Time from queue to delivery
- **Error Rate**: Failed notifications by error type
- **Queue Length**: Celery task queue backlog

### Alerts
- High failure rate for any channel
- SMTP/SMS provider API errors
- Queue backlog exceeding threshold
- Template rendering errors

## Performance Optimization

### Scaling
- **Horizontal Scaling**: Multiple worker instances
- **Queue Partitioning**: Separate queues by priority/channel
- **Connection Pooling**: Efficient SMTP connections
- **Template Caching**: Cache compiled templates

### Optimization
- **Batch Processing**: Group similar notifications
- **Provider Failover**: Automatic failover between providers
- **Content Compression**: Compress large email content
- **Async Processing**: Non-blocking notification delivery

## Documentation
- **OpenAPI Spec**: `/api/notifications/openapi.json`
- **Swagger UI**: `/api/notifications/docs`
- **Template Guide**: Documentation for creating custom templates
- **Provider Setup**: Integration guides for email/SMS providers