# Profile Service

## Overview
The Profile Service is a Python/FastAPI-based service that manages user profiles, avatars, and profile history tracking.

## Features
- 👤 **User Profiles** - Complete user profile management with customizable fields
- 🖼️ **Avatar Management** - Upload and manage user profile pictures via MinIO
- 📊 **Profile History** - Track all profile changes with timestamps
- 🔗 **Presigned URLs** - Secure file upload via presigned URLs
- 🔍 **Profile Search** - Search and filter user profiles

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: MinIO (S3-compatible object storage)
- **Authentication**: JWT token validation
- **Database Migrations**: Alembic
- **Image Processing**: PIL/Pillow for avatar optimization

## API Endpoints

### Protected Endpoints (JWT Required)
- `GET /api/profile/me` - Get current user's profile
- `PUT /api/profile/me` - Update current user's profile
- `POST /api/profile/avatar/presign` - Get presigned URL for avatar upload
- `PUT /api/profile/avatar` - Update avatar URL after upload
- `DELETE /api/profile/avatar` - Remove user avatar
- `GET /api/profile/history` - Get profile change history
- `GET /api/profile/{user_id}` - Get specific user's profile (if public)

### Public Endpoints
- `GET /api/profile/healthz` - Health check

## Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
JWT_SECRET_KEY=your-jwt-secret-key
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio-access-key
MINIO_SECRET_KEY=minio-secret-key
MINIO_SECURE=false
MINIO_BUCKET_NAME=avatars
MAX_AVATAR_SIZE=5242880  # 5MB
ALLOWED_AVATAR_TYPES=image/jpeg,image/png,image/webp
```

## Database Schema
- **profiles** - User profile data (bio, location, website, etc.)
- **profile_history** - Audit log of all profile changes
- **avatar_uploads** - Track avatar upload metadata

## Profile Fields
```json
{
  "user_id": "uuid",
  "display_name": "string",
  "bio": "string",
  "location": "string", 
  "website": "url",
  "avatar_url": "url",
  "is_public": "boolean",
  "social_links": {
    "twitter": "string",
    "linkedin": "string", 
    "github": "string"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Avatar Upload Flow
1. **Request Presigned URL**: `POST /api/profile/avatar/presign`
   ```json
   {
     "filename": "avatar.jpg",
     "content_type": "image/jpeg",
     "size": 1024000
   }
   ```

2. **Upload to MinIO**: Use returned presigned URL to upload file directly

3. **Update Profile**: `PUT /api/profile/avatar`
   ```json
   {
     "avatar_url": "https://minio.example.com/avatars/user-123/avatar.jpg"
   }
   ```

## Security Features
- 🔒 **JWT Authentication** - All profile operations require valid tokens
- 📁 **File Validation** - Strict file type and size limits for avatars
- 🔗 **Presigned URLs** - Secure direct upload to object storage
- 📊 **Audit Trail** - Complete history of profile changes
- 🛡️ **Privacy Controls** - Public/private profile visibility settings

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

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Test avatar upload flow
pytest tests/test_avatar.py -v
```

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Built from Python 3.12 slim
- **Health Checks**: `/healthz` and `/readyz` endpoints
- **Migrations**: Automatic via init container
- **File Storage**: MinIO integration for avatar storage
- **Monitoring**: Prometheus metrics at `/metrics`

## Documentation
- **OpenAPI Spec**: `/api/profile/openapi.json`
- **Swagger UI**: `/api/profile/docs`
- **API Gateway Integration**: Accessible via `/api/profile/*` routes