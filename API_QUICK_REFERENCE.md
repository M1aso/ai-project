# API Quick Reference Guide

## Service Overview

| Service | Port | Technology | Base URL | Primary Function |
|---------|------|------------|----------|------------------|
| Auth | 8001 | Python FastAPI | `/api/auth` | Authentication & authorization |
| Chat | 8002 | Node.js TypeScript | `/ws`, `/api/chats` | Real-time messaging |
| Content | 8003 | Go | `/api` | Course & content management |
| Profile | 8004 | Python FastAPI | `/api/profile` | User profile management |
| Notifications | 8005 | Python FastAPI | `/api` | Multi-channel notifications |
| Analytics | 8006 | Python FastAPI | `/api/analytics` | Event tracking & reporting |
| Content Worker | - | Python | Background | Content processing |

## Authentication Flow

1. **Register/Login** → Get access & refresh tokens
2. **Use Access Token** → Include in `Authorization: Bearer <token>` header
3. **Refresh Token** → Get new access token when expired

## Key Endpoints Quick Reference

### Auth Service
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/phone/send-code` - Send SMS verification
- `POST /api/auth/phone/verify` - Verify SMS and get tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout and invalidate tokens

### Profile Service
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile
- `POST /api/profile/avatar/presign` - Upload avatar

### Content Service
- `GET /api/courses` - List courses
- `POST /api/courses` - Create course
- `GET /api/courses/{id}` - Get course details
- `POST /api/materials/{id}/upload/presign` - Upload content

### Chat Service
- `GET /ws?token=<token>&roomId=<id>` - WebSocket connection
- `GET /api/chats/{id}/messages` - Message history
- `GET /api/chats/search` - Search chats

### Notifications Service
- `POST /api/notify/send` - Send notification
- `GET /api/subscriptions` - Get user preferences
- `PUT /api/subscriptions` - Update preferences

### Analytics Service
- `POST /api/analytics/ingest` - Send events
- `GET /api/analytics/dashboard` - Get metrics
- `GET /api/analytics/reports/events` - Export data

## Common Response Formats

### Success Response
```json
{
  "data": { ... },
  "status": "success"
}
```

### Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

### Token Response
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 900
}
```

## Status Codes

| Code | Meaning | Usage |
|------|---------|--------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 202 | Accepted | Async operation queued |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limited |
| 500 | Internal Server Error | Server error |

## Rate Limits

| Endpoint Type | Limit | Window |
|---------------|--------|--------|
| Auth endpoints | 10 req/min | Per IP |
| API endpoints | 1000 req/hour | Per user |
| File uploads | 10 uploads/hour | Per user |
| Analytics | 100 batches/min | Per user |

## WebSocket Events

### Chat Messages
```json
{
  "type": "message",
  "content": "Hello!",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### System Events
```json
{
  "type": "user_joined",
  "user_id": "123",
  "username": "john_doe"
}
```

## Common Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
X-Request-ID: unique-request-id
```

## Environment Variables

### Development
```bash
AUTH_API_URL=http://localhost:8001
CHAT_API_URL=http://localhost:8002
CONTENT_API_URL=http://localhost:8003
```

### Production
```bash
AUTH_API_URL=https://auth.api.example.com
CHAT_API_URL=https://chat.api.example.com
CONTENT_API_URL=https://content.api.example.com
```

## Testing Commands

### cURL Examples
```bash
# Login
curl -X POST "https://api.example.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Get profile
curl -H "Authorization: Bearer <token>" \
  "https://api.example.com/api/profile"

# Send notification
curl -X POST "https://api.example.com/api/notify/send" \
  -H "Content-Type: application/json" \
  -d '{"channel": "email", "recipient": "user@example.com", "template": "welcome"}'
```

## JavaScript Client Example

```javascript
class APIClient {
    constructor(baseURL, token) {
        this.baseURL = baseURL;
        this.token = token;
    }

    async request(method, endpoint, data) {
        const response = await fetch(`${this.baseURL}${endpoint}`, {
            method,
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: data ? JSON.stringify(data) : undefined
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        
        return await response.json();
    }
}

// Usage
const client = new APIClient('https://api.example.com', 'your-token');
const profile = await client.request('GET', '/api/profile');
```

---

For complete documentation with detailed examples, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md).