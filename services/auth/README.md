# Auth Service

## Overview
The Auth Service is a Python/FastAPI-based authentication and authorization service that handles user registration, login, JWT token management, and session control.

## Features
- 🔐 **User Registration & Login** - Email-based authentication with secure password hashing
- 🎫 **JWT Token Management** - Access and refresh tokens with configurable expiration
- 📧 **Email Verification** - User account verification via email
- 🔄 **Password Reset** - Secure password reset flow with email tokens
- 👥 **Session Management** - Track and manage user sessions
- 🛡️ **Admin Operations** - Administrative user management endpoints

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with HS256 algorithm
- **Password Hashing**: Bcrypt
- **Database Migrations**: Alembic
- **Email**: SMTP integration (configurable)

## API Endpoints

### Public Endpoints (No Authentication)
- `POST /api/auth/email/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/password/reset/request` - Request password reset
- `POST /api/auth/password/reset/confirm` - Confirm password reset
- `POST /api/auth/email/verify` - Verify email address
- `GET /api/auth/test/public` - Public test endpoint

### Protected Endpoints (JWT Required)
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout current session
- `POST /api/auth/logout-all` - Logout all sessions
- `POST /api/auth/refresh` - Refresh JWT token
- `GET /api/auth/sessions` - List user sessions
- `DELETE /api/auth/sessions/{session_id}` - Delete specific session
- `GET /api/auth/test/protected` - Protected test endpoint

### Admin Endpoints (Admin Role Required)
- `GET /api/auth/admin/users` - List all users

## Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Database Schema
- **users** - User accounts with email, hashed passwords, roles
- **user_sessions** - Active user sessions for logout management
- **password_reset_tokens** - Temporary tokens for password reset
- **email_verification_tokens** - Tokens for email verification

## Security Features
- 🔒 **Secure Password Storage** - Bcrypt hashing with salt
- 🎫 **JWT Token Security** - Signed tokens with expiration
- 📧 **Email Verification** - Prevent unauthorized account creation
- 🔄 **Token Rotation** - Refresh token mechanism
- 🛡️ **Session Management** - Track and revoke sessions
- ⚠️ **Rate Limiting** - Protection against brute force attacks

## Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest
```

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Built from Python 3.12 slim
- **Health Checks**: `/healthz` and `/readyz` endpoints
- **Migrations**: Automatic via init container
- **Monitoring**: Prometheus metrics at `/metrics`

## Documentation
- **OpenAPI Spec**: `/api/auth/openapi.json`
- **Swagger UI**: `/api/auth/docs`
- **API Gateway Integration**: Accessible via `/api/auth/*` routes