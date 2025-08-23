# Corrected API Endpoints Reference

## 🚨 Issues Found and Fixed

### Problems Identified from Terminal Output:
1. **API Gateway routing mismatch** - Services were not properly routed through the gateway
2. **Service path inconsistencies** - Different services used different base paths
3. **Documentation inconsistencies** - Wrong ports and paths in documentation
4. **Missing health check endpoints** - Some services lacked proper health checks

## ✅ Corrected Service Endpoints

### Base Gateway URL
- **API Gateway**: `http://api.45.146.164.70.nip.io`

### Service Health Checks
All services now expose health checks at both direct and API paths:

```bash
# Health check endpoints (through API Gateway)
curl http://api.45.146.164.70.nip.io/api/auth/healthz
curl http://api.45.146.164.70.nip.io/api/profile/healthz
curl http://api.45.146.164.70.nip.io/api/content/healthz
curl http://api.45.146.164.70.nip.io/api/notifications/healthz
curl http://api.45.146.164.70.nip.io/api/analytics/healthz
```

### Auth Service (`/api/auth`)
```bash
# Health check
curl http://api.45.146.164.70.nip.io/api/auth/healthz

# Phone authentication
curl -X POST http://api.45.146.164.70.nip.io/api/auth/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567"}'

curl -X POST http://api.45.146.164.70.nip.io/api/auth/phone/verify \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567", "code": "123456"}'

# Email authentication
curl -X POST http://api.45.146.164.70.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Profile Service (`/api/profile`)
```bash
# Health check
curl http://api.45.146.164.70.nip.io/api/profile/healthz

# Get profile (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://api.45.146.164.70.nip.io/api/profile

# Update profile
curl -X PUT http://api.45.146.164.70.nip.io/api/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name": "John", "city": "New York"}'
```

### Content Service (`/api/content`)
```bash
# Health check
curl http://api.45.146.164.70.nip.io/api/content/healthz

# List courses
curl http://api.45.146.164.70.nip.io/api/content/courses

# Create course (requires auth token)
curl -X POST http://api.45.146.164.70.nip.io/api/content/courses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Course", "description": "Course description"}'
```

### Notifications Service (`/api/notifications`)
```bash
# Health check
curl http://api.45.146.164.70.nip.io/api/notifications/healthz

# Send notification
curl -X POST http://api.45.146.164.70.nip.io/api/notifications/notify/send \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "template": "welcome_email",
    "data": {"user_name": "John Doe"}
  }'

# Get user subscriptions (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://api.45.146.164.70.nip.io/api/notifications/subscriptions
```

### Chat Service (`/api/chats`)
```bash
# WebSocket connection
ws://api.45.146.164.70.nip.io/ws?token=YOUR_TOKEN&roomId=room123

# Get message history
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://api.45.146.164.70.nip.io/api/chats/room123/messages

# Search chats
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://api.45.146.164.70.nip.io/api/chats/search?q=hello"
```

### Analytics Service (`/api/analytics`)
```bash
# Health check
curl http://api.45.146.164.70.nip.io/api/analytics/healthz

# Ingest events (requires auth token)
curl -X POST http://api.45.146.164.70.nip.io/api/analytics/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{
    "ts": "2024-01-15T10:30:00Z",
    "user_id": "user123",
    "type": "page_view",
    "src": "web_app",
    "payload": {"page": "/dashboard"}
  }]'

# Get dashboard metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://api.45.146.164.70.nip.io/api/analytics/dashboard
```

## 🔧 Changes Made

### 1. API Gateway Configuration
- **Fixed routing**: Updated Envoy configuration to properly route requests
- **Content service**: Fixed prefix rewrite to `/api/content`
- **Notifications**: Added proper routing for `/api/notifications`
- **Chat service**: Added routing for both `/api/chat` and `/api/chats`

### 2. Service Implementations
- **Content service**: Added health check endpoints at both `/healthz` and `/api/content/healthz`
- **Standardized ports**: All services now use port 8000 consistently
- **Improved responses**: Added proper JSON headers and structured responses

### 3. Documentation Updates
- **API_QUICK_REFERENCE.md**: Fixed service ports and base URLs
- **QUICK_START.md**: Updated test commands with correct endpoints
- **Added health checks**: All services now have documented health check endpoints

## 🧪 Testing the Fixed Endpoints

### Quick Health Check Test
```bash
#!/bin/bash
echo "Testing all service health checks..."

services=("auth" "profile" "content" "notifications" "analytics")
base_url="http://api.45.146.164.70.nip.io/api"

for service in "${services[@]}"; do
  echo -n "Testing $service: "
  response=$(curl -s -w "%{http_code}" "$base_url/$service/healthz")
  if [[ "$response" =~ 200$ ]]; then
    echo "✅ OK"
  else
    echo "❌ FAILED (HTTP: ${response: -3})"
  fi
done

echo -n "Testing content courses: "
response=$(curl -s -w "%{http_code}" "$base_url/content/courses")
if [[ "$response" =~ 200$ ]]; then
  echo "✅ OK"
else
  echo "❌ FAILED (HTTP: ${response: -3})"
fi
```

### Authentication Flow Test
```bash
#!/bin/bash
echo "Testing authentication flow..."

# Test phone verification
echo "1. Sending SMS code..."
curl -X POST http://api.45.146.164.70.nip.io/api/auth/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567"}'

echo -e "\n\n2. Test login endpoint..."
curl -X POST http://api.45.146.164.70.nip.io/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## 🚀 Next Steps

1. **Deploy the changes**: Push these changes to trigger redeployment
2. **Verify services**: Run the test scripts above to verify all endpoints work
3. **Update client applications**: Update any frontend/mobile apps with the corrected endpoints
4. **Monitor logs**: Check service logs for any remaining routing issues

## 📋 Service Status Checklist

- [x] API Gateway routing configuration fixed
- [x] Content service routing fixed
- [x] Notifications service routing added
- [x] Chat service routing (both /chat and /chats)
- [x] Health check endpoints standardized
- [x] Documentation updated with correct endpoints
- [x] Port numbers standardized (all use 8000)
- [x] Test commands provided for verification
