# Content Service

## Overview
The Content Service is a Go-based service that manages educational content including courses, learning materials, and media assets with real database operations and JWT authentication.

## Features
- 📚 **Course Management** - Create, read, update courses with status tracking
- 📄 **Learning Materials** - Manage materials linked to course sections
- 🎥 **Media Assets** - Handle video/audio content with transcoding support
- 🔗 **Presigned URLs** - Secure file upload via MinIO integration
- 🔒 **JWT Authentication** - Secure API access with token validation
- 🛠️ **Service Integration** - API endpoints for content-worker communication

## Technology Stack
- **Language**: Go 1.21
- **Framework**: Chi router with middleware
- **Database**: PostgreSQL with direct SQL queries
- **Authentication**: JWT token validation + Service API keys
- **File Storage**: MinIO (S3-compatible object storage)
- **Database Migrations**: Goose migration tool

## API Endpoints

### Public Endpoints
- `GET /healthz` - Health check
- `GET /api/content/healthz` - Service health check
- `GET /api/content/openapi.json` - OpenAPI specification
- `GET /api/content/docs` - Swagger UI documentation

### Protected Endpoints (JWT Required)
- `GET /api/content/courses` - List all courses
- `POST /api/content/courses` - Create new course
- `GET /api/content/courses/{id}` - Get specific course
- `PUT /api/content/courses/{id}` - Update course status
- `GET /api/content/materials` - List all materials
- `POST /api/content/materials` - Create new material
- `GET /api/content/materials/{id}` - Get specific material
- `PUT /api/content/materials/{id}` - Update material status
- `POST /api/content/materials/{id}/upload/presign` - Get presigned upload URL

### Service Endpoints (Service API Key Required)
- `PATCH /api/content/media-assets/{id}` - Update asset status (used by content-worker)

## Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname?sslmode=disable
JWT_SECRET_KEY=your-jwt-secret-key
CONTENT_WORKER_API_KEY=service-api-key
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio-access-key
MINIO_SECRET_KEY=minio-secret-key
MINIO_SECURE=false
PORT=8000
LOG_LEVEL=DEBUG
```

## Database Schema

### Courses Table
```sql
CREATE TABLE courses (
    id VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    status VARCHAR DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Materials Table
```sql
CREATE TABLE materials (
    id VARCHAR PRIMARY KEY,
    section_id VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Media Assets Table
```sql
CREATE TABLE media_assets (
    id VARCHAR PRIMARY KEY,
    material_id VARCHAR REFERENCES materials(id),
    url VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Authentication

### JWT Authentication (User Requests)
```go
Authorization: Bearer <jwt-token>
```
Used for all user-facing endpoints. Token must contain:
- `sub`: User ID
- `roles`: User roles array
- `type`: "access"

### Service API Key (Internal Communication)
```go
Authorization: Bearer <service-api-key>
```
Used for content-worker to update asset status. Provides service-level access.

## API Examples

### Create Course
```bash
curl -X POST "http://api.example.com/api/content/courses" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to Go",
    "description": "Learn Go programming language",
    "category": "programming"
  }'
```

### Get Presigned Upload URL
```bash
curl -X POST "http://api.example.com/api/content/materials/mat-123/upload/presign" \
  -H "Authorization: Bearer <jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "size": 10485760,
    "type": "video/mp4"
  }'
```

### Update Asset Status (Content-Worker)
```bash
curl -X PATCH "http://api.example.com/api/content/media-assets/asset-123" \
  -H "Authorization: Bearer <service-api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "ready",
    "renditions": {
      "720p": "https://minio.example.com/videos/asset-123_720p.m3u8"
    }
  }'
```

## Development

### Prerequisites
- Go 1.21+
- PostgreSQL database
- MinIO server (for file storage)

### Setup
```bash
# Install dependencies
go mod download

# Run database migrations
./migrate -database "postgres://..." -path ./internal/db/migrations up

# Start development server
go run cmd/server/main.go

# Build for production
go build -o content-service cmd/server/main.go
```

### Running Migrations
```bash
# Create new migration
goose -dir internal/db/migrations create add_new_table sql

# Run migrations
goose -dir internal/db/migrations postgres "postgres://..." up

# Check status
goose -dir internal/db/migrations postgres "postgres://..." status
```

## Testing
```bash
# Run all tests
go test ./...

# Run tests with coverage
go test -cover ./...

# Run specific test package
go test ./internal/service/...
```

## Content-Worker Integration
The Content Service provides endpoints for the Content-Worker service to update media asset status after transcoding:

1. **Content-Worker** processes video files
2. **Updates asset status** via `/api/content/media-assets/{id}` endpoint
3. **Uses service API key** for authentication
4. **Provides rendition URLs** for different quality levels

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Built from Go with migration tool included
- **Health Checks**: `/healthz` endpoint
- **Migrations**: Run via separate Kubernetes job
- **File Storage**: MinIO integration for media assets
- **Monitoring**: Built-in logging and error tracking

## Documentation
- **OpenAPI Spec**: `/api/content/openapi.json`
- **Swagger UI**: `/api/content/docs`
- **API Gateway Integration**: Accessible via `/api/content/*` routes

## Security Features
- 🔒 **JWT Authentication** - All user endpoints require valid tokens
- 🔑 **Service API Keys** - Secure service-to-service communication
- 📁 **File Validation** - Strict file type and size validation
- 🔗 **Presigned URLs** - Secure direct upload to object storage
- 🛡️ **SQL Injection Protection** - Parameterized queries throughout