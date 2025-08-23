# Authentication Service Testing Guide

This guide provides comprehensive testing instructions for your authentication service, including local testing, integration testing, and production-ready testing scenarios.

## 🚀 Quick Start Testing

### Method 1: Automated Test Script

```bash
# Make sure the auth service is running
cd services/auth

# Run the complete test suite
python scripts/test_auth_flow.py

# Or run specific tests
python scripts/test_auth_flow.py --test register
python scripts/test_auth_flow.py --test login
python scripts/test_auth_flow.py --test rate-limit
```

### Method 2: Docker Compose Testing

```bash
# Start all services including MailHog
docker-compose -f docker-compose.test.yml up -d

# View MailHog web interface for emails
open http://localhost:8025

# Run tests against the containerized service
docker-compose -f docker-compose.test.yml run test-runner

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

## 📧 Email Testing Setup

### Option 1: MailHog (Recommended for Development)

MailHog captures emails without sending them, perfect for testing.

1. **Start MailHog:**
```bash
# Using Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Or download binary from https://github.com/mailhog/MailHog
```

2. **Configure Environment:**
```bash
export SMTP_HOST=localhost
export SMTP_PORT=1025
export SMTP_USE_TLS=false
export FROM_EMAIL=noreply@testapp.com
```

3. **Test Registration Flow:**
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "device_info": {"platform": "test"}
  }'

# Check email at http://localhost:8025
# Copy verification token from email
```

### Option 2: Real SMTP Service

For production-like testing with services like Gmail, SendGrid, or AWS SES:

1. **Gmail Setup (App Password Required):**
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USE_TLS=true
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export FROM_EMAIL=your-email@gmail.com
```

2. **SendGrid Setup:**
```bash
export SMTP_HOST=smtp.sendgrid.net
export SMTP_PORT=587
export SMTP_USE_TLS=true
export SMTP_USERNAME=apikey
export SMTP_PASSWORD=your-sendgrid-api-key
export FROM_EMAIL=verified-sender@yourdomain.com
```

## 📱 Manual Testing Scenarios

### Complete User Journey

1. **Registration:**
```bash
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -H "User-Agent: TestApp/1.0" \
  -d '{
    "email": "newuser@example.com",
    "password": "MySecure123!",
    "device_info": {
      "platform": "web",
      "browser": "Chrome",
      "version": "120.0",
      "mobile": false
    }
  }'
```

2. **Check Email and Verify:**
```bash
# Get token from email/MailHog, then:
curl -X POST http://localhost:8000/api/auth/email/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your-verification-token-here"
  }'
```

3. **Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "MySecure123!",
    "remember_me": true,
    "device_info": {
      "platform": "mobile",
      "os": "iOS",
      "version": "17.0"
    }
  }'
```

4. **Access Protected Resource:**
```bash
# Use access_token from login response
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### Security Testing

1. **Password Validation:**
```bash
# Test weak passwords (should fail)
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "123456"}'

curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password"}'
```

2. **Rate Limiting:**
```bash
# Test login rate limiting (should block after 5 attempts)
for i in {1..10}; do
  echo "Attempt $i:"
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "wrongpass"}' | jq .
  sleep 1
done
```

3. **Email Validation:**
```bash
# Test disposable email domains (should fail)
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@10minutemail.com", "password": "SecurePass123!"}'
```

### Session Management Testing

1. **Multiple Sessions:**
```bash
# Login from different "devices"
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "User-Agent: iPhone/1.0" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "device_info": {"platform": "mobile", "os": "iOS"}
  }'

curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "User-Agent: Chrome/1.0" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "device_info": {"platform": "web", "browser": "Chrome"}
  }'
```

2. **View Sessions:**
```bash
curl -X GET http://localhost:8000/api/auth/sessions \
  -H "Authorization: Bearer your_access_token"
```

3. **Logout from All Devices:**
```bash
curl -X POST http://localhost:8000/api/auth/logout-all \
  -H "Authorization: Bearer your_access_token"
```

## 🧪 Automated Testing

### Unit Tests

```bash
cd services/auth
python -m pytest tests/ -v
```

### Integration Tests

Create comprehensive integration tests:

```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_complete_registration_flow(client):
    # Test registration
    with patch('services.auth.app.services.email_service.email_service.send_verification_email') as mock_email:
        mock_email.return_value = True
        
        response = client.post("/api/auth/email/register", json={
            "email": "integration@test.com",
            "password": "TestPass123!",
            "device_info": {"platform": "test"}
        })
        assert response.status_code == 200
        mock_email.assert_called_once()
    
    # Get verification token from database
    # ... implementation ...
    
    # Test verification
    verify_response = client.post("/api/auth/email/verify", json={
        "token": verification_token
    })
    assert verify_response.status_code == 200
    
    tokens = verify_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert "session_id" in tokens
    
    # Test protected endpoint
    profile_response = client.get("/api/auth/profile", headers={
        "Authorization": f"Bearer {tokens['access_token']}"
    })
    assert profile_response.status_code == 200
```

### Load Testing

Use tools like `locust` or `artillery` for load testing:

```python
# locustfile.py
from locust import HttpUser, task, between

class AuthUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Register and login
        response = self.client.post("/api/auth/email/register", json={
            "email": f"user{self.user_id}@test.com",
            "password": "TestPass123!"
        })
        # ... complete flow ...
    
    @task
    def login(self):
        self.client.post("/api/auth/login", json={
            "email": f"user{self.user_id}@test.com",
            "password": "TestPass123!"
        })
    
    @task
    def profile(self):
        if hasattr(self, 'access_token'):
            self.client.get("/api/auth/profile", headers={
                "Authorization": f"Bearer {self.access_token}"
            })
```

Run load test:
```bash
pip install locust
locust -f locustfile.py --host http://localhost:8000
```

## 🔍 Monitoring and Debugging

### Health Checks

```bash
# Service health
curl http://localhost:8000/healthz

# API health
curl http://localhost:8000/api/auth/healthz

# Metrics
curl http://localhost:8000/metrics
```

### Database Inspection

```bash
# Connect to database
psql postgresql://auth_user:auth_pass@localhost:5432/auth_db

# Check users
SELECT id, email, is_active, created_at FROM users;

# Check verification tokens
SELECT token, user_id, expires_at FROM email_verifications;

# Check sessions (Redis)
redis-cli -h localhost -p 6379
AUTH redis_password
KEYS session:*
KEYS user_sessions:*
```

### Logs Analysis

```bash
# View application logs
docker logs auth-service

# Follow logs in real-time
docker logs -f auth-service

# Filter for specific patterns
docker logs auth-service 2>&1 | grep "ERROR\|WARN"
```

## 🚨 Troubleshooting Common Issues

### Email Not Sending

1. **Check SMTP Configuration:**
```bash
# Test SMTP connection
python -c "
import smtplib
server = smtplib.SMTP('localhost', 1025)
print('SMTP connection successful')
server.quit()
"
```

2. **Check MailHog:**
- Web UI: http://localhost:8025
- SMTP server: localhost:1025

### Database Connection Issues

```bash
# Test database connection
python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://auth_user:auth_pass@localhost:5432/auth_db')
conn = engine.connect()
print('Database connection successful')
conn.close()
"
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli -h localhost -p 6379 ping
redis-cli -h localhost -p 6379 -a redis_password ping
```

### Rate Limiting Not Working

1. **Check Redis Connection:**
```bash
redis-cli -h localhost -p 6379 -a redis_password
KEYS login_attempts:*
```

2. **Clear Rate Limit Data:**
```bash
redis-cli -h localhost -p 6379 -a redis_password
FLUSHDB
```

## 📊 Performance Testing

### Benchmark Authentication

```bash
# Using Apache Bench
ab -n 1000 -c 10 -T 'application/json' -p login.json http://localhost:8000/api/auth/login

# login.json content:
# {"email": "user@example.com", "password": "SecurePass123!"}
```

### Database Performance

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
WHERE mean_exec_time > 100 
ORDER BY mean_exec_time DESC;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public';
```

## ✅ Production Readiness Checklist

- [ ] All tests pass
- [ ] Email service configured and tested
- [ ] Rate limiting working correctly
- [ ] Database migrations tested
- [ ] SSL/TLS certificates configured
- [ ] Environment variables secured
- [ ] Monitoring and alerting set up
- [ ] Backup and recovery tested
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation updated

Your authentication service is now ready for comprehensive testing! 🎉
