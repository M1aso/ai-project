# Content Service

The Content Service is responsible for managing courses, sections, materials, and media assets in the AI e-learning platform.

## Features

- **Course Management**: Create, read, update courses with status transitions
- **Material Management**: Handle learning materials with different types (video, text, etc.)
- **File Upload**: Presigned URL generation for secure file uploads to MinIO
- **Status Workflow**: Draft → Review → Published workflow for content approval

## API Endpoints

### Health Check
- `GET /api/content/healthz` - Service health check

### Courses
- `GET /api/content/courses` - List all courses
- `POST /api/content/courses` - Create a new course
- `GET /api/content/courses/{id}` - Get course by ID
- `PUT /api/content/courses/{id}` - Update course status

### Materials
- `GET /api/content/materials` - List all materials
- `GET /api/content/materials/{id}` - Get material by ID
- `PUT /api/content/materials/{id}` - Update material status

### File Upload
- `POST /api/content/materials/{id}/upload/presign` - Get presigned upload URL

## Database Schema

The service uses PostgreSQL with the following tables:

- `courses` - Course information with created_at/updated_at timestamps
- `sections` - Course sections with created_at/updated_at timestamps
- `materials` - Learning materials with created_at/updated_at timestamps
- `media_assets` - File attachments with created_at/updated_at timestamps
- `tags` - Course tags with created_at/updated_at timestamps
- `course_tags` - Many-to-many relationship between courses and tags

## Status Transitions

Both courses and materials follow the same workflow:
- `draft` → `review`
- `review` → `published` or `draft`
- `published` → (no transitions allowed)

## Technology Stack

- **Language**: Go 1.21
- **Framework**: Chi router
- **Database**: PostgreSQL
- **Storage**: MinIO for file uploads
- **Documentation**: OpenAPI 3.0 with Swagger UI

## Development

The service exposes OpenAPI documentation at:
- `/api/content/docs` - Swagger UI
- `/api/content/openapi.json` - OpenAPI specification

## Environment Variables

- `PORT` - Service port (default: 8000)
- `DATABASE_URL` - PostgreSQL connection string
- `MINIO_ENDPOINT` - MinIO server endpoint
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key