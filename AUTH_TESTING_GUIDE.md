# 🔐 Authentication Service Testing Guide

## Overview
This guide will help you test the complete authentication and registration email flow in your AI Project. The auth service includes:

- **User Registration** with email verification
- **Secure Login** with JWT tokens
- **Session Management** across devices
- **Password Reset** functionality
- **Rate Limiting** and security features

## 🚀 Quick Start Testing

### Option 1: Use the Built-in Test Script (Recommended)

Your project already includes a comprehensive test script at `services/auth/scripts/test_auth_flow.py`. This script tests the complete flow automatically.

```bash
# Navigate to auth service
cd services/auth

# Run the complete test suite
python scripts/test_auth_flow.py

# Or run specific tests
python scripts/test_auth_flow.py --test register
python scripts/test_auth_flow.py --test verify
python scripts/test_auth_flow.py --test login
```

### Option 2: Manual Testing with cURL

#### 1. Test Service Health
```bash
curl http://localhost:8000/healthz
```

#### 2. Register a New User
```bash
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -H "User-Agent: TestClient/1.0" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "device_info": {
      "platform": "web",
      "browser": "Chrome",
      "version": "120.0"
    }
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful. Please check your email for verification.",
  "email": "test@example.com"
}
```

#### 3. Check Email Verification
The verification email will be sent to MailHog (if running) or your configured SMTP service.

**MailHog Access:**
- Web UI: http://localhost:8025
- SMTP: localhost:1025

#### 4. Verify Email with Token
```bash
curl -X POST http://localhost:8000/api/auth/email/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "your_verification_token_here"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "session_id": "session_uuid_here",
  "message": "Email verified successfully"
}
```

#### 5. Login with Verified Account
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "remember_me": true,
    "device_info": {
      "platform": "web",
      "browser": "Chrome",
      "version": "120.0"
    }
  }'
```

#### 6. Access Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## 🐳 Docker Setup for Testing

### Start Required Services

```bash
# Start PostgreSQL and Redis
docker compose -f docker-compose.dev.yml up -d postgres redis

# Start MailHog for email testing
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog

# Or use the test docker-compose
cd services/auth
docker compose -f docker-compose.test.yml up -d
```

### Environment Configuration

Create a `.env` file in `services/auth/` with:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/aiproject

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-here-use-openssl-rand-base64-32

# Email (MailHog for testing)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USE_TLS=false
FROM_EMAIL=noreply@testapp.com

# API
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## 🧪 Testing Scenarios

### 1. Complete Registration Flow
```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "password": "SecurePass123!"}'

# 2. Check MailHog at http://localhost:8025
# 3. Copy verification token from email
# 4. Verify email
curl -X POST http://localhost:8000/api/auth/email/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN_FROM_EMAIL"}'

# 5. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "newuser@example.com", "password": "SecurePass123!"}'
```

### 2. Password Reset Flow
```bash
# 1. Request password reset
curl -X POST http://localhost:8000/api/auth/password/reset/request \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Check MailHog for reset token
# 3. Reset password
curl -X POST http://localhost:8000/api/auth/password/reset/confirm \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_EMAIL",
    "new_password": "NewSecurePass123!"
  }'
```

### 3. Session Management
```bash
# Get access token first (from login)
ACCESS_TOKEN="your_access_token_here"

# List all sessions
curl -X GET http://localhost:8000/api/auth/sessions \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Logout from specific session
curl -X DELETE http://localhost:8000/api/auth/sessions/SESSION_ID \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Logout from all devices
curl -X POST http://localhost:8000/api/auth/logout-all \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 4. Rate Limiting Test
```bash
# Test login rate limiting
for i in {1..10}; do
  echo "Attempt $i:"
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrongpassword"}' \
    | jq .
  sleep 1
done
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database connection
psql -h localhost -U postgres -d aiproject
```

#### 2. Redis Connection Error
```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli -h localhost ping
```

#### 3. Email Not Sending
```bash
# Check MailHog is running
docker ps | grep mailhog

# Check MailHog UI at http://localhost:8025
# Check SMTP logs
docker logs mailhog
```

#### 4. JWT Token Issues
```bash
# Verify JWT_SECRET_KEY is set
echo $JWT_SECRET_KEY

# Generate new secret if needed
openssl rand -base64 32
```

### Debug Mode

Enable debug logging in your `.env`:

```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 Test Results Validation

### Expected Test Outcomes

1. **Registration**: ✅ 200 OK with success message
2. **Email Verification**: ✅ 200 OK with JWT tokens
3. **Login**: ✅ 200 OK with JWT tokens
4. **Protected Endpoint**: ✅ 200 OK with user data
5. **Session Management**: ✅ 200 OK with session list
6. **Rate Limiting**: ✅ 429 Too Many Requests after 5 attempts
7. **Password Reset**: ✅ 200 OK with success message

### Performance Benchmarks

- **Registration**: < 500ms
- **Email Verification**: < 300ms
- **Login**: < 400ms
- **Protected Endpoint**: < 200ms

## 🚀 Production Testing

### Security Testing
```bash
# Test SQL injection protection
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com\"; DROP TABLE users; --", "password": "SecurePass123!"}'

# Test XSS protection
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "<script>alert(\"xss\")</script>@example.com", "password": "SecurePass123!"}'
```

### Load Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test registration endpoint
ab -n 100 -c 10 -p test_data.json -T application/json http://localhost:8000/api/auth/email/register
```

## 📝 Test Data

### Valid Test Emails
- `test@example.com`
- `user@testdomain.org`
- `admin@company.co.uk`

### Invalid Test Emails
- `invalid-email`
- `@nodomain.com`
- `user@.com`
- `user@disposable-email.com`

### Valid Passwords
- `SecurePass123!`
- `MyP@ssw0rd`
- `Str0ng#P@ss`

### Invalid Passwords
- `123456` (too short)
- `password` (no uppercase, numbers, special chars)
- `Password` (no numbers, special chars)

## 🎯 Next Steps

After successful testing:

1. **Configure Production SMTP** (SendGrid, AWS SES, etc.)
2. **Set up Monitoring** (Prometheus, Grafana)
3. **Configure SSL/TLS** certificates
4. **Set up Backup** and disaster recovery
5. **Implement OAuth** providers (Google, GitHub)
6. **Add 2FA/TOTP** support

## 📚 Additional Resources

- [AUTH_USER_GUIDE.md](services/auth/AUTH_USER_GUIDE.md) - Detailed user guide
- [SECURITY_SETUP.md](services/auth/SECURITY_SETUP.md) - Security configuration
- [TESTING_GUIDE.md](services/auth/TESTING_GUIDE.md) - Service-specific testing
- [API Documentation](http://localhost:8000/docs) - Swagger UI when service is running

---

**Happy Testing! 🚀**

Your authentication service is well-architected with enterprise-grade security features. This testing guide will help ensure everything works correctly before going to production.
