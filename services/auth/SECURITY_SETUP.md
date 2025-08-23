# Authentication Service Security Setup

## Overview

This document outlines the security improvements implemented in the authentication service and provides setup instructions.

## Security Features Implemented

### 1. **Password Security**
- ✅ **bcrypt hashing** instead of SHA-256
- ✅ **Salt-based password storage**
- ✅ **Strong password validation**

### 2. **Token Security**
- ✅ **JWT tokens** with proper claims
- ✅ **Access/Refresh token rotation**
- ✅ **Token expiration and validation**
- ✅ **Secure token generation**

### 3. **Rate Limiting & Brute Force Protection**
- ✅ **Redis-backed rate limiting**
- ✅ **Progressive delays** for failed attempts
- ✅ **IP-based and user-based limits**
- ✅ **Memory fallback** when Redis unavailable

### 4. **Session Management**
- ✅ **Secure session tracking**
- ✅ **Device fingerprinting**
- ✅ **Session revocation**
- ✅ **Multi-device support**

### 5. **Input Validation**
- ✅ **Comprehensive password validation**
- ✅ **Email domain validation**
- ✅ **Phone number validation**
- ✅ **Device info sanitization**

### 6. **Security Headers**
- ✅ **CORS protection**
- ✅ **XSS protection**
- ✅ **Content Security Policy**
- ✅ **HSTS headers**

## Setup Instructions

### Prerequisites

1. **Python 3.12+**
2. **Redis server** (for rate limiting and sessions)
3. **PostgreSQL** (recommended) or SQLite (development)

### Installation

1. **Install dependencies:**
   ```bash
   cd services/auth
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Configure Redis:**
   ```bash
   # Install Redis
   sudo apt-get install redis-server
   
   # Start Redis
   sudo systemctl start redis-server
   
   # Enable Redis on startup
   sudo systemctl enable redis-server
   ```

4. **Set up database:**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

### Environment Configuration

#### Critical Security Variables

```bash
# Generate a secure JWT secret key
JWT_SECRET_KEY=$(openssl rand -base64 32)

# Database (use PostgreSQL in production)
DATABASE_URL=postgresql://user:password@localhost:5432/auth_db

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-redis-password
```

#### Optional Security Variables

```bash
# Rate limiting
MAX_LOGIN_ATTEMPTS=5
RATE_LIMIT_WINDOW=3600

# Session management
SESSION_TTL=2592000

# Password hashing
BCRYPT_ROUNDS=12
```

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t auth-service .
   ```

2. **Run with environment variables:**
   ```bash
   docker run -d \
     --name auth-service \
     -p 8000:8000 \
     -e JWT_SECRET_KEY=your-secret-key \
     -e DATABASE_URL=postgresql://user:pass@db:5432/auth \
     -e REDIS_HOST=redis \
     auth-service
   ```

3. **Using Docker Compose:**
   ```yaml
   version: '3.8'
   services:
     auth:
       build: .
       ports:
         - "8000:8000"
       environment:
         - JWT_SECRET_KEY=your-secret-key
         - DATABASE_URL=postgresql://user:pass@db:5432/auth
         - REDIS_HOST=redis
       depends_on:
         - db
         - redis
     
     db:
       image: postgres:15
       environment:
         POSTGRES_DB: auth
         POSTGRES_USER: user
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     redis:
       image: redis:7-alpine
       command: redis-server --requirepass your-redis-password
   
   volumes:
     postgres_data:
   ```

## API Endpoints

### New Secure Endpoints (Recommended)

- `POST /api/auth/email/register` - Secure registration
- `POST /api/auth/login` - Secure login with session management
- `POST /api/auth/logout` - Logout with session cleanup
- `POST /api/auth/logout-all` - Logout from all devices
- `GET /api/auth/sessions` - Get user sessions
- `DELETE /api/auth/sessions/{session_id}` - Revoke specific session
- `POST /api/auth/password/reset/request` - Password reset request
- `POST /api/auth/password/reset/confirm` - Password reset confirmation
- `GET /api/auth/profile` - Protected profile endpoint

### Legacy Endpoints (Backward Compatibility)

The original endpoints in `/api/auth/email/*` are still available but lack the enhanced security features.

## Security Testing

### Test Rate Limiting

```bash
# Test login rate limiting
for i in {1..10}; do
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrongpassword"}'
done
```

### Test Password Validation

```bash
# Test weak password rejection
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

### Test Session Management

```bash
# Login and get session
response=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}')

# Extract tokens and session_id from response
# Use session_id to test session endpoints
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Failed login attempts per IP/user**
2. **Rate limit violations**
3. **Token validation failures**
4. **Session anomalies**
5. **Password reset requests**

### Prometheus Metrics

The service exposes metrics at `/metrics`:
- `auth_request_total` - Total HTTP requests
- `auth_request_latency_seconds` - Request latency
- Custom rate limiting metrics (to be added)

### Recommended Alerts

1. **High failed login rate** (>50 failures/hour per IP)
2. **Unusual session patterns** (multiple concurrent sessions)
3. **Token validation failures** (potential attack)
4. **Database connection failures**
5. **Redis connection failures**

## Security Best Practices

### Production Deployment

1. **Use HTTPS only** - Never deploy without SSL/TLS
2. **Secure JWT secrets** - Use environment variables, never hardcode
3. **Database security** - Use connection pooling, SSL, and proper credentials
4. **Redis security** - Enable authentication, use SSL if possible
5. **Network security** - Use firewalls, VPNs, or private networks
6. **Logging** - Log all authentication events for audit
7. **Backup** - Regular database and Redis backups
8. **Updates** - Keep dependencies updated

### Ongoing Security

1. **Regular security audits**
2. **Penetration testing**
3. **Dependency vulnerability scanning**
4. **Log analysis and monitoring**
5. **Incident response procedures**

## Troubleshooting

### Common Issues

1. **Redis connection failures:**
   - Check Redis service status
   - Verify network connectivity
   - Check authentication credentials

2. **JWT validation errors:**
   - Verify JWT_SECRET_KEY consistency
   - Check token expiration
   - Validate token format

3. **Rate limiting issues:**
   - Check Redis connectivity
   - Verify rate limit configuration
   - Clear rate limit data if needed

4. **Database connection issues:**
   - Check DATABASE_URL format
   - Verify database credentials
   - Check network connectivity

### Debug Commands

```bash
# Check Redis connectivity
redis-cli -h localhost -p 6379 ping

# Check database connectivity
psql $DATABASE_URL -c "SELECT 1"

# View application logs
docker logs auth-service

# Check rate limit data
redis-cli -h localhost -p 6379 keys "login_attempts:*"
```

## Migration from Legacy System

### Steps to Migrate

1. **Deploy new service** alongside existing one
2. **Update client applications** to use new endpoints
3. **Migrate existing user data** (password hashes need re-hashing)
4. **Test thoroughly** with gradual traffic migration
5. **Monitor** for issues during transition
6. **Decommission** legacy endpoints after full migration

### Password Migration

Since the new system uses bcrypt instead of SHA-256, existing passwords need to be migrated:

1. **Option 1:** Force password reset for all users
2. **Option 2:** Hybrid validation (check old hash, update to new hash on successful login)
3. **Option 3:** Background migration with user notification

## Support and Maintenance

### Regular Maintenance Tasks

1. **Clean up expired tokens** (automated)
2. **Rotate JWT secrets** (quarterly)
3. **Update dependencies** (monthly)
4. **Review security logs** (weekly)
5. **Performance monitoring** (continuous)

### Emergency Procedures

1. **Security breach response**
2. **Mass session revocation**
3. **Rate limit adjustment**
4. **Service rollback procedures**
5. **Database recovery**
