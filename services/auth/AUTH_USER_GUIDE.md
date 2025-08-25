# Authentication Service - User Guide & Testing

## How Your Auth Service Works

Your authentication service provides secure user authentication with two sets of endpoints:

### 🔐 **Security Features**
- **bcrypt password hashing** with salt
- **JWT tokens** (access + refresh tokens)
- **Redis-backed rate limiting** with progressive delays
- **Session management** with device tracking
- **Input validation** and sanitization
- **Security headers** (CORS, XSS protection, etc.)
- **Brute force protection**

### 📡 **Available Endpoints**

#### **Secure Endpoints** (Recommended - `/api/auth/`)
- `POST /api/auth/email/register` - Enhanced registration
- `POST /api/auth/email/verify` - Email verification
- `POST /api/auth/login` - Secure login with sessions
- `POST /api/auth/logout` - Logout with session cleanup
- `POST /api/auth/logout-all` - Logout from all devices
- `GET /api/auth/sessions` - Get user sessions
- `DELETE /api/auth/sessions/{session_id}` - Revoke session
- `POST /api/auth/password/reset/request` - Password reset
- `POST /api/auth/password/reset/confirm` - Confirm reset
- `GET /api/auth/me` - Get current user authentication info

#### **Legacy Endpoints** (Basic - `/api/auth/email/`)
- `POST /api/auth/email/register` - Basic registration
- `POST /api/auth/email/verify` - Basic verification
- `POST /api/auth/login` - Basic login
- `POST /api/auth/password/reset/request` - Basic reset request
- `POST /api/auth/password/reset/confirm` - Basic reset confirm

---

## 🚀 **User Authentication Flow**

### **1. Registration Flow**

```bash
# Step 1: Register user
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -H "User-Agent: MyApp/1.0" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "device_info": {
      "platform": "web",
      "browser": "Chrome",
      "version": "120.0"
    }
  }'
```

**Response:**
```json
{
  "message": "Registration successful. Please check your email for verification.",
  "email": "user@example.com"
}
```

**What happens:**
1. Password is validated (8+ chars, uppercase, lowercase, digit, special char)
2. Email domain is checked (no disposable emails)
3. Password is hashed with bcrypt
4. User created with `is_active=false`
5. Verification token generated (24h expiry)
6. Event emitted for email notification

### **2. Email Verification**

```bash
# Step 2: Verify email (token from database or email)
curl -X POST http://localhost:8000/api/auth/email/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "verification_token_here"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "session_id": "session_uuid_here",
  "message": "Email verified successfully"
}
```

### **3. Login Flow**

```bash
# Step 3: Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "remember_me": true,
    "device_info": {
      "platform": "mobile",
      "os": "iOS",
      "version": "17.0"
    }
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "session_id": "session_uuid_here",
  "message": "Login successful"
}
```

### **4. Accessing Protected Resources**

```bash
# Use access token in Authorization header
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### **5. Session Management**

```bash
# Get all user sessions
curl -X GET http://localhost:8000/api/auth/sessions \
  -H "Authorization: Bearer your_access_token"

# Logout from specific session
curl -X DELETE http://localhost:8000/api/auth/sessions/session_id \
  -H "Authorization: Bearer your_access_token"

# Logout from all devices
curl -X POST http://localhost:8000/api/auth/logout-all \
  -H "Authorization: Bearer your_access_token"
```

---

## 🧪 **Testing with Real Services**

### **Option 1: Email Testing with MailHog (Recommended)**

1. **Install MailHog:**
```bash
# Using Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Or download binary from https://github.com/mailhog/MailHog
```

2. **Add Email Service Integration:**
```python
# Add to services/auth/app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", 1025))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
    def send_verification_email(self, email: str, token: str):
        msg = MIMEMultipart()
        msg['From'] = "noreply@yourapp.com"
        msg['To'] = email
        msg['Subject'] = "Verify Your Email"
        
        verification_url = f"http://localhost:8000/api/auth/email/verify?token={token}"
        body = f"""
        Please click the link to verify your email:
        {verification_url}
        
        Or use this token: {token}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.smtp_username:
                server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"Verification email sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

email_service = EmailService()
```

3. **Integrate with Registration:**
```python
# Update services/auth/app/services/email_flows.py
from .email_service import email_service

def register(db: Session, email: str, password: str) -> str:
    # ... existing code ...
    db.commit()
    
    # Send verification email
    email_service.send_verification_email(email, token)
    
    return token
```

4. **Test Flow:**
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123!"}'

# Check MailHog UI at http://localhost:8025 for the email
# Click the verification link or copy the token
```

### **Option 2: SMS Testing with Twilio**

1. **Install Twilio SDK:**
```bash
pip install twilio
```

2. **Add SMS Service:**
```python
# Add to services/auth/app/services/sms_service.py
from twilio.rest import Client
import os

class SMSService:
    def __init__(self):
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.client = Client(account_sid, auth_token) if account_sid else None
        
    def send_verification_code(self, phone: str, code: str):
        if not self.client:
            print(f"SMS Mock: Code {code} for {phone}")
            return
            
        try:
            message = self.client.messages.create(
                body=f"Your verification code is: {code}",
                from_=self.from_number,
                to=phone
            )
            print(f"SMS sent to {phone}: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

sms_service = SMSService()
```

3. **Add Phone Authentication Endpoints:**
```python
# Add to services/auth/app/routers/secure_auth.py
@router.post("/phone/send-code")
async def send_phone_code(
    request: Request,
    req: PhoneCodeRequest,
    db: Session = Depends(get_db)
):
    """Send verification code to phone."""
    # Generate 6-digit code
    code = f"{random.randint(100000, 999999)}"
    
    # Store code in database with expiry
    # ... implementation ...
    
    # Send SMS
    sms_service.send_verification_code(req.phone, code)
    
    return {"message": "Verification code sent"}

@router.post("/phone/verify-code")
async def verify_phone_code(
    request: Request,
    req: PhoneVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify phone code and create account."""
    # Verify code from database
    # Create user account
    # Return tokens
    pass
```

### **Option 3: Integration Testing Setup**

1. **Create Test Environment:**
```python
# tests/test_integration.py
import pytest
import smtplib
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

@pytest.fixture
def mock_email():
    with patch('smtplib.SMTP') as mock_smtp:
        yield mock_smtp

def test_full_registration_flow(client, mock_email):
    # Test registration
    response = client.post("/api/auth/email/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 200
    
    # Verify email was "sent"
    mock_email.assert_called_once()
    
    # Get token from database
    # ... implementation ...
    
    # Test verification
    verify_response = client.post("/api/auth/email/verify", json={
        "token": verification_token
    })
    assert verify_response.status_code == 200
    assert "access_token" in verify_response.json()
```

### **Option 4: Development Testing Tools**

1. **Create Testing Script:**
```python
# scripts/test_auth.py
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_registration_flow():
    # Register
    print("🔐 Testing Registration...")
    response = requests.post(f"{BASE_URL}/api/auth/email/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "device_info": {"platform": "test", "browser": "script"}
    })
    print(f"Registration: {response.status_code} - {response.json()}")
    
    # Get verification token (in real app, this comes from email)
    # For testing, you can query the database directly
    print("\n📧 Check your email/MailHog for verification token")
    token = input("Enter verification token: ")
    
    # Verify
    print("✅ Testing Verification...")
    verify_response = requests.post(f"{BASE_URL}/api/auth/email/verify", json={
        "token": token
    })
    print(f"Verification: {verify_response.status_code} - {verify_response.json()}")
    
    if verify_response.status_code == 200:
        tokens = verify_response.json()
        access_token = tokens["access_token"]
        
        # Test protected endpoint
        print("\n🔒 Testing Protected Endpoint...")
        profile_response = requests.get(f"{BASE_URL}/api/auth/profile", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(f"Profile: {profile_response.status_code} - {profile_response.json()}")

if __name__ == "__main__":
    test_registration_flow()
```

2. **Run Testing Script:**
```bash
python scripts/test_auth.py
```

---

## 🔧 **Missing Components to Add**

### **1. Email Notification Service**
```python
# Add this to services/auth/app/services/email_flows.py
from .email_service import email_service
from ..events import emit_user_registered, emit_password_reset

def register(db: Session, email: str, password: str) -> str:
    # ... existing code ...
    db.commit()
    
    # Send verification email
    email_service.send_verification_email(email, token)
    
    # Emit event for other services
    emit_user_registered(email)
    
    return token

def request_password_reset(db: Session, email: str) -> str:
    # ... existing code ...
    db.commit()
    
    # Send password reset email
    email_service.send_password_reset_email(email, token)
    
    # Emit event
    emit_password_reset(email)
    
    return token
```

### **2. Phone Authentication**
- Add phone number validation
- SMS service integration
- Phone verification flow
- Phone-based login

### **3. OAuth Integration**
- Google OAuth
- GitHub OAuth  
- Apple Sign-In

### **4. Enhanced Security**
- 2FA/TOTP support
- Device fingerprinting
- Geolocation tracking
- Suspicious activity detection

---

## 🚨 **Rate Limiting & Security Testing**

### **Test Rate Limiting:**
```bash
# Test login rate limiting (should block after 5 attempts)
for i in {1..10}; do
  echo "Attempt $i:"
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrongpassword"}' \
    | jq .
  sleep 1
done
```

### **Test Password Validation:**
```bash
# Test weak password (should fail)
curl -X POST http://localhost:8000/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}' \
  | jq .
```

### **Test Session Management:**
```bash
# Login and get multiple sessions
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' \
  | jq .access_token | xargs -I {} \
  curl -X GET http://localhost:8000/api/auth/sessions \
  -H "Authorization: Bearer {}"
```

---

## 🎯 **Production Checklist**

- [ ] Set up proper SMTP service (SendGrid, AWS SES, etc.)
- [ ] Configure Redis for production
- [ ] Set up PostgreSQL database
- [ ] Configure proper JWT secrets
- [ ] Set up monitoring and alerting
- [ ] Configure CORS for your frontend domains
- [ ] Set up SSL/TLS certificates
- [ ] Configure rate limiting for production load
- [ ] Set up backup and disaster recovery
- [ ] Implement proper logging and audit trails

Your authentication service is well-structured with enterprise-grade security features! 🚀
