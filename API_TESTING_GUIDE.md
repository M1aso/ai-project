# 🔐 API Testing Guide - Authentication Flow

Complete guide for testing the authentication API endpoints with examples.

## 📊 API Documentation

**Swagger UI**: `http://api.45.146.164.70.nip.io/docs` (when deployed)
**OpenAPI Schema**: `http://api.45.146.164.70.nip.io/openapi.json`

## 🔑 Authentication Flow

### 1. Register New User (Public)

```bash
curl -X POST "http://api.45.146.164.70.nip.io/api/auth/email/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful. Please check your email for verification.",
  "email": "testuser@example.com"
}
```

### 2. Verify Email (Public)

**Option A: Click link in email** (GET request)
```
http://api.45.146.164.70.nip.io/api/auth/email/verify?token=YOUR_TOKEN_HERE
```

**Option B: API verification** (POST request)
```bash
curl -X POST "http://api.45.146.164.70.nip.io/api/auth/email/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN_FROM_EMAIL"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
  "session_id": "02c8e432-1500-4c16-b0ef-f65cf309ea48",
  "message": "Email verified successfully! You can now log in."
}
```

### 3. Login (Public)

```bash
curl -X POST "http://api.45.146.164.70.nip.io/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "remember_me": false
  }'
```

## 🔒 Protected Endpoints

Use the `access_token` from verification/login in the Authorization header:

### Get Current User Info

```bash
curl -X GET "http://api.45.146.164.70.nip.io/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
  "email": "testuser@example.com",
  "is_active": true,
  "login_type": "email",
  "created_at": "2025-08-25T09:20:21.381740+00:00",
  "message": "Authentication successful!"
}
```

### Get User Profile

```bash
curl -X GET "http://api.45.146.164.70.nip.io/api/auth/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "profile": {
    "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
    "email": "testuser@example.com",
    "is_active": true,
    "login_type": "email",
    "created_at": "2025-08-25T09:20:21.381740+00:00",
    "updated_at": "2025-08-25T09:20:21.381740+00:00"
  },
  "stats": {
    "pending_verifications": 0,
    "account_age_days": 0
  },
  "message": "Profile retrieved successfully"
}
```

## 🧪 Test Endpoints

### Public Test Endpoint

```bash
curl -X GET "http://api.45.146.164.70.nip.io/api/auth/test/public"
```

**Expected Response:**
```json
{
  "message": "This is a public endpoint - no authentication required",
  "timestamp": "2025-08-25T09:58:00.000000+00:00",
  "status": "public"
}
```

### Protected Test Endpoint

```bash
curl -X GET "http://api.45.146.164.70.nip.io/api/auth/test/protected" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "message": "Hello testuser@example.com! This endpoint requires authentication.",
  "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
  "timestamp": "2025-08-25T09:58:00.000000+00:00",
  "status": "authenticated"
}
```

## 👑 Admin Endpoints

### List All Users (Admin Only)

```bash
curl -X GET "http://api.45.146.164.70.nip.io/api/auth/admin/users?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ADMIN_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "users": [
    {
      "user_id": "f1338a69-aed4-499f-a5ae-214d9cf1c7c6",
      "email": "testuser@example.com",
      "is_active": true,
      "login_type": "email",
      "created_at": "2025-08-25T09:20:21.381740+00:00"
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 10,
    "offset": 0,
    "has_more": false
  },
  "message": "Retrieved 1 users"
}
```

## 🚨 Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 429 Rate Limited
```json
{
  "detail": "Too many requests"
}
```

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

## 📋 Complete Testing Script

Here's a complete bash script to test the entire authentication flow:

```bash
#!/bin/bash

BASE_URL="http://api.45.146.164.70.nip.io/api/auth"
EMAIL="test-$(date +%s)@example.com"
PASSWORD="TestPassword123!"

echo "=== Testing Authentication Flow ==="
echo "Email: $EMAIL"
echo

# 1. Test public endpoint
echo "1. Testing public endpoint..."
curl -s "$BASE_URL/test/public" | jq .
echo

# 2. Register user
echo "2. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/email/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
echo $REGISTER_RESPONSE | jq .
echo

# 3. Get verification token from database (for testing)
echo "3. Get verification token from database..."
TOKEN=$(PGPASSWORD=postgres123 psql -h localhost -p 15432 -U postgres -d aiproject -t -c \
  "SELECT token FROM email_verifications ORDER BY created_at DESC LIMIT 1;" | xargs)
echo "Token: $TOKEN"
echo

# 4. Verify email
echo "4. Verifying email..."
VERIFY_RESPONSE=$(curl -s "$BASE_URL/email/verify?token=$TOKEN")
echo $VERIFY_RESPONSE | jq .

# Extract access token
ACCESS_TOKEN=$(echo $VERIFY_RESPONSE | jq -r .access_token)
echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo

# 5. Test protected endpoint
echo "5. Testing protected endpoint..."
curl -s -X GET "$BASE_URL/test/protected" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo

# 6. Get user info
echo "6. Getting user info..."
curl -s -X GET "$BASE_URL/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
echo

# 7. Test without token (should fail)
echo "7. Testing protected endpoint without token (should fail)..."
curl -s -X GET "$BASE_URL/test/protected" | jq .
echo

echo "=== Testing Complete ==="
```

## 🔍 Debugging Tips

### Check Email in MailHog
- **Web UI**: `http://mailhog.45.146.164.70.nip.io`
- **API**: `curl http://mailhog.45.146.164.70.nip.io/api/v2/messages`

### Check Database
```bash
# SSH tunnel to database
ssh -L 15432:localhost:5432 user@server

# Connect to database
PGPASSWORD=postgres123 psql -h localhost -p 15432 -U postgres -d aiproject

# Check users
SELECT id, email, is_active, created_at FROM users ORDER BY created_at DESC LIMIT 5;

# Check verification tokens
SELECT token, user_id, expires_at FROM email_verifications ORDER BY created_at DESC LIMIT 5;
```

### JWT Token Analysis
Use [jwt.io](https://jwt.io) to decode and inspect JWT tokens.

### Service Health
```bash
curl http://api.45.146.164.70.nip.io/api/auth/healthz
```

---

## 📖 Swagger UI Features

The Swagger UI (`/docs`) provides:
- 📝 **Interactive API Documentation**
- 🔐 **Built-in Authentication** (click "Authorize" button)
- 🧪 **Test Requests** directly from the browser
- 📊 **Request/Response Examples**
- 🏷️ **Organized by Tags**:
  - **Public Endpoints** - No authentication required
  - **Protected Endpoints** - Require JWT token
  - **Admin Endpoints** - Require admin privileges  
  - **Test Endpoints** - For development testing

### Using Swagger UI Authentication

1. Go to `http://api.45.146.164.70.nip.io/docs`
2. Register a new user via `/email/register`
3. Verify email via `/email/verify` (get token from MailHog)
4. Copy the `access_token` from the response
5. Click the **"Authorize"** button in Swagger UI
6. Enter: `Bearer YOUR_ACCESS_TOKEN`
7. Now you can test all protected endpoints!

This provides a complete testing environment for developers! 🚀
