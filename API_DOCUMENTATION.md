# Comprehensive API Documentation

## Overview

This document provides comprehensive documentation for all public APIs, functions, and components in the microservices architecture. The system consists of 7 core services:

- **Auth Service** - Authentication and authorization
- **Chat Service** - Real-time messaging and chat functionality
- **Content Service** - Course and content management
- **Profile Service** - User profile management
- **Notifications Service** - Multi-channel notification delivery
- **Analytics Service** - Event tracking and reporting
- **Content Worker Service** - Background content processing

## Architecture Overview

The system follows a microservices architecture pattern where each service is independently deployable and has its own database. Services communicate via HTTP APIs and are designed to be stateless and horizontally scalable.

### Technology Stack
- **Python Services**: FastAPI, SQLAlchemy, Pydantic, Alembic
- **Node.js Services**: TypeScript, WebSocket support
- **Go Services**: Native Go with HTTP routing
- **Shared Contracts**: OpenAPI 3.1 specifications

---

## Authentication Service (Auth API)

**Version**: 0.2.0  
**Base URL**: `/api/auth`  
**Technology**: Python FastAPI

### Overview
The Auth service handles user authentication, registration, and account management. It supports both phone and email-based authentication flows with SMS and email verification.

### Authentication Flow
The service uses JWT tokens with access/refresh token pairs:
- **Access Token**: Short-lived token for API requests
- **Refresh Token**: Long-lived token for obtaining new access tokens

### Public Endpoints

#### Phone Authentication

##### Send SMS Code
```http
POST /api/auth/phone/send-code
```

Sends a verification code via SMS to the provided phone number.

**Request Body:**
```json
{
  "phone": "+1234567890"
}
```

**Response:**
- `200 OK` - Code sent successfully
- `400 Bad Request` - Invalid phone number format
- `429 Too Many Requests` - Rate limit exceeded

**Example:**
```bash
curl -X POST "https://api.example.com/api/auth/phone/send-code" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+1234567890"}'
```

##### Verify SMS Code
```http
POST /api/auth/phone/verify
```

Verifies the SMS code and optionally creates a new account. Issues access and refresh tokens upon successful verification.

**Request Body:**
```json
{
  "phone": "+1234567890",
  "code": "123456",
  "email": "user@example.com",     // Optional: for new account creation
  "password": "securePassword123"  // Optional: for new account creation
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Status Codes:**
- `200 OK` - Verification successful, tokens issued
- `400 Bad Request` - Invalid request format
- `401 Unauthorized` - Invalid code or expired
- `423 Locked` - Account locked due to multiple failed attempts
- `429 Too Many Requests` - Rate limit exceeded

#### Email Authentication

##### Register with Email
```http
POST /api/auth/email/register
```

Registers a new user with email and password. Sends a verification email.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
- `200 OK` - Verification email sent
- `400 Bad Request` - Invalid email format or weak password
- `429 Too Many Requests` - Rate limit exceeded

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Example:**
```bash
curl -X POST "https://api.example.com/api/auth/email/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

##### Verify Email
```http
POST /api/auth/email/verify
```

Verifies email registration token and activates the account.

**Request Body:**
```json
{
  "token": "email-verification-token-here"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

##### Login with Email
```http
POST /api/auth/login
```

Authenticates user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "remember_me": false  // Optional: extends refresh token lifetime
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Password Management

##### Request Password Reset
```http
POST /api/auth/password/reset/request
```

Sends a password reset email to the user.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
- `200 OK` - Reset email sent (always returns 200 for security)

##### Confirm Password Reset
```http
POST /api/auth/password/reset/confirm
```

Resets password using the token from the reset email.

**Request Body:**
```json
{
  "token": "password-reset-token",
  "new_password": "newSecurePassword123"
}
```

**Response:**
- `200 OK` - Password updated successfully
- `400 Bad Request` - Invalid token format or weak password
- `401 Unauthorized` - Invalid or expired token

#### Token Management

##### Refresh Access Token
```http
POST /api/auth/refresh
```

Obtains a new access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

##### Logout
```http
POST /api/auth/logout
```

Invalidates the refresh token and logs out the user.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
- `204 No Content` - Successfully logged out

#### Account Management

##### Request Email Update
```http
POST /api/auth/email/update/request
```

Requests to change the account email address. Requires authentication.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": "newemail@example.com"
}
```

##### Confirm Email Update
```http
POST /api/auth/email/update/confirm
```

Confirms the email update using the verification token.

**Request Body:**
```json
{
  "token": "email-update-token"
}
```

##### Update Phone Number

Send code for phone update:
```http
POST /api/auth/phone/update/send-code
```

Verify phone update:
```http
POST /api/auth/phone/update/verify
```

### Error Handling

All endpoints return consistent error responses:

```json
{
  "code": "ERROR_CODE",
  "message": "Human readable error message"
}
```

**Common Error Codes:**
- `INVALID_REQUEST` - Malformed request
- `INVALID_CREDENTIALS` - Wrong email/password
- `ACCOUNT_LOCKED` - Too many failed attempts
- `TOKEN_EXPIRED` - JWT token expired
- `TOKEN_INVALID` - Malformed or invalid token
- `RATE_LIMIT_EXCEEDED` - Too many requests

### Security Considerations

1. **Rate Limiting**: All endpoints are rate-limited to prevent abuse
2. **Account Locking**: Accounts are temporarily locked after multiple failed login attempts
3. **Token Expiration**: Access tokens expire after 15 minutes, refresh tokens after 30 days
4. **Secure Headers**: All responses include security headers (HSTS, CSP, etc.)
5. **Input Validation**: All inputs are validated and sanitized

---

## Chat Service (Chat API)

**Version**: 0.2.0  
**Base URL**: `/api/chats`  
**Technology**: Node.js TypeScript

### Overview
The Chat service provides real-time messaging capabilities using WebSockets for live communication and HTTP APIs for message history and chat management.

### Authentication
All endpoints require a valid JWT access token from the Auth service.

**Headers:**
```
Authorization: Bearer <access_token>
```

### WebSocket Connection

#### Establish WebSocket Connection
```
GET /ws?token=<access_token>&roomId=<room_id>
```

Establishes a WebSocket connection for real-time messaging.

**Parameters:**
- `token` (required): JWT access token
- `roomId` (required): Chat room identifier

**Response:**
- `101 Switching Protocols` - WebSocket connection established
- `401 Unauthorized` - Invalid token
- `403 Forbidden` - No access to the specified room

**Example:**
```javascript
const ws = new WebSocket('wss://api.example.com/ws?token=ACCESS_TOKEN&roomId=room123');

ws.onopen = function() {
    console.log('Connected to chat');
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};

// Send a message
ws.send(JSON.stringify({
    type: 'message',
    content: 'Hello, World!',
    timestamp: new Date().toISOString()
}));
```

#### WebSocket Message Format

**Outgoing Messages (Client to Server):**
```json
{
  "type": "message",
  "content": "Hello, World!",
  "timestamp": "2024-01-15T10:30:00Z",
  "reply_to": "message_id_optional"
}
```

**Incoming Messages (Server to Client):**
```json
{
  "id": "msg_123456",
  "type": "message",
  "user_id": "user_789",
  "username": "john_doe",
  "content": "Hello, World!",
  "timestamp": "2024-01-15T10:30:00Z",
  "reply_to": null
}
```

**System Messages:**
```json
{
  "type": "user_joined",
  "user_id": "user_789",
  "username": "john_doe",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### HTTP Endpoints

#### Get Message History
```http
GET /api/chats/{chatId}/messages
```

Retrieves message history for a specific chat room.

**Parameters:**
- `chatId` (path, required): Chat room identifier
- `limit` (query, optional): Number of messages to retrieve (default: 50, max: 100)
- `offset` (query, optional): Number of messages to skip (default: 0)

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_123456",
      "user_id": "user_789",
      "username": "john_doe",
      "content": "Hello, World!",
      "timestamp": "2024-01-15T10:30:00Z",
      "reply_to": null
    }
  ],
  "total": 150,
  "has_more": true
}
```

**Example:**
```bash
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  "https://api.example.com/api/chats/room123/messages?limit=20&offset=0"
```

#### Search Chats
```http
GET /api/chats/search
```

Searches for chat rooms by name or description.

**Parameters:**
- `q` (query, required): Search query string

**Response:**
```json
{
  "chats": [
    {
      "id": "room123",
      "name": "General Discussion",
      "description": "Main chat room for general topics",
      "member_count": 25,
      "last_activity": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get User Presence
```http
GET /api/chats/presence/{userId}
```

Checks if a specific user is currently online.

**Parameters:**
- `userId` (path, required): User identifier

**Response:**
```json
{
  "online": true,
  "last_seen": "2024-01-15T10:30:00Z"
}
```

### Real-time Features

1. **Live Messaging**: Instant message delivery via WebSocket
2. **User Presence**: Real-time online/offline status
3. **Typing Indicators**: Shows when users are typing
4. **Message Reactions**: React to messages with emojis
5. **File Sharing**: Upload and share files in chat

### Usage Examples

#### Complete Chat Integration

```javascript
class ChatClient {
    constructor(accessToken, roomId) {
        this.token = accessToken;
        this.roomId = roomId;
        this.ws = null;
    }

    async connect() {
        // Load message history first
        const history = await this.getMessageHistory();
        this.displayMessages(history.messages);

        // Establish WebSocket connection
        this.ws = new WebSocket(`wss://api.example.com/ws?token=${this.token}&roomId=${this.roomId}`);
        
        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleIncomingMessage(message);
        };
    }

    async getMessageHistory(limit = 50, offset = 0) {
        const response = await fetch(
            `https://api.example.com/api/chats/${this.roomId}/messages?limit=${limit}&offset=${offset}`,
            {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            }
        );
        return await response.json();
    }

    sendMessage(content, replyTo = null) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'message',
                content: content,
                timestamp: new Date().toISOString(),
                reply_to: replyTo
            }));
        }
    }

    handleIncomingMessage(message) {
        // Handle different message types
        switch (message.type) {
            case 'message':
                this.displayMessage(message);
                break;
            case 'user_joined':
                this.showUserJoined(message);
                break;
            case 'user_left':
                this.showUserLeft(message);
                break;
        }
    }
}

// Usage
const chat = new ChatClient('your-access-token', 'room123');
chat.connect();
```

---

## Content Service (Content API)

**Version**: 0.2.0  
**Base URL**: `/api`  
**Technology**: Go

### Overview
The Content service manages educational content including courses, sections, materials, and media assets. It provides a hierarchical content structure with support for different material types and upload management.

### Authentication
All endpoints require a valid JWT access token from the Auth service.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Data Models

#### Course
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Introduction to Programming",
  "description": "Learn the basics of programming",
  "status": "published"  // draft, review, published
}
```

#### Section
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174001",
  "course_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Variables and Data Types",
  "sequence": 1
}
```

#### Material
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
  "section_id": "123e4567-e89b-12d3-a456-426614174001",
  "type": "video",  // video, document
  "title": "Introduction to Variables",
  "status": "published"
}
```

### Course Management

#### List Courses
```http
GET /api/courses
```

Retrieves all courses available to the authenticated user.

**Response:**
```json
{
  "courses": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Introduction to Programming",
      "description": "Learn the basics of programming",
      "status": "published",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Course
```http
POST /api/courses
```

Creates a new course.

**Request Body:**
```json
{
  "title": "Advanced JavaScript",
  "description": "Deep dive into JavaScript concepts",
  "status": "draft"
}
```

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174003",
  "title": "Advanced JavaScript",
  "description": "Deep dive into JavaScript concepts",
  "status": "draft",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Course
```http
GET /api/courses/{id}
```

Retrieves a specific course by ID.

**Parameters:**
- `id` (path, required): Course UUID

**Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Introduction to Programming",
  "description": "Learn the basics of programming",
  "status": "published",
  "sections": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "title": "Variables and Data Types",
      "sequence": 1,
      "material_count": 3
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Update Course
```http
PUT /api/courses/{id}
```

Updates an existing course.

**Request Body:**
```json
{
  "title": "Introduction to Programming - Updated",
  "description": "Updated description",
  "status": "published"
}
```

#### Delete Course
```http
DELETE /api/courses/{id}
```

Deletes a course and all its associated content.

**Response:**
- `204 No Content` - Course deleted successfully

### Section Management

#### List Course Sections
```http
GET /api/courses/{courseId}/sections
```

Retrieves all sections for a specific course.

**Parameters:**
- `courseId` (path, required): Course UUID

**Response:**
```json
{
  "sections": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "course_id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Variables and Data Types",
      "sequence": 1,
      "material_count": 3,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Create Section
```http
POST /api/courses/{courseId}/sections
```

Creates a new section within a course.

**Request Body:**
```json
{
  "title": "Functions and Scope",
  "sequence": 2
}
```

#### Update Section
```http
PUT /api/sections/{id}
```

Updates an existing section.

#### Delete Section
```http
DELETE /api/sections/{id}
```

Deletes a section and all its materials.

### Material Management

#### List Section Materials
```http
GET /api/sections/{sectionId}/materials
```

Retrieves all materials for a specific section.

**Response:**
```json
{
  "materials": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174002",
      "section_id": "123e4567-e89b-12d3-a456-426614174001",
      "type": "video",
      "title": "Introduction to Variables",
      "status": "published",
      "media_assets": [
        {
          "id": "asset_123",
          "url": "https://cdn.example.com/video.mp4",
          "status": "ready"
        }
      ]
    }
  ]
}
```

#### Create Material
```http
POST /api/sections/{sectionId}/materials
```

Creates a new material within a section.

**Request Body:**
```json
{
  "type": "video",
  "title": "Advanced Functions",
  "status": "draft"
}
```

#### Get Material
```http
GET /api/materials/{id}
```

Retrieves a specific material with its media assets.

#### Update Material
```http
PUT /api/materials/{id}
```

Updates material metadata.

#### Delete Material
```http
DELETE /api/materials/{id}
```

Deletes a material and its associated media assets.

### Media Upload Management

#### Presign Upload URL
```http
POST /api/materials/{id}/upload/presign
```

Generates a presigned URL for uploading media content directly to cloud storage.

**Parameters:**
- `id` (path, required): Material UUID

**Request Body:**
```json
{
  "content_type": "video/mp4",
  "file_size": 1048576,
  "file_name": "lesson1.mp4"
}
```

**Response:**
```json
{
  "upload_url": "https://storage.example.com/upload-url-with-signature",
  "media_asset_id": "asset_123",
  "expires_at": "2024-01-15T11:30:00Z"
}
```

#### Upload Process Flow

1. **Request presigned URL** from the API
2. **Upload file directly** to cloud storage using the presigned URL
3. **Notify the API** that upload is complete (optional webhook)
4. **Media asset status** automatically updates from "uploading" to "ready"

**Example Upload Flow:**
```javascript
async function uploadMaterial(materialId, file) {
    // Step 1: Get presigned URL
    const presignResponse = await fetch(`/api/materials/${materialId}/upload/presign`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content_type: file.type,
            file_size: file.size,
            file_name: file.name
        })
    });
    
    const { upload_url, media_asset_id } = await presignResponse.json();
    
    // Step 2: Upload directly to cloud storage
    const uploadResponse = await fetch(upload_url, {
        method: 'PUT',
        body: file,
        headers: {
            'Content-Type': file.type
        }
    });
    
    if (uploadResponse.ok) {
        console.log('Upload successful, media asset ID:', media_asset_id);
        return media_asset_id;
    }
}
```

### Media Asset Management

#### Get Media Asset
```http
GET /api/media-assets/{id}
```

Retrieves metadata and access information for a media asset.

**Response:**
```json
{
  "id": "asset_123",
  "material_id": "123e4567-e89b-12d3-a456-426614174002",
  "url": "https://cdn.example.com/video.mp4",
  "status": "ready",
  "file_size": 1048576,
  "content_type": "video/mp4",
  "duration": 300,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Tag Management

#### List Tags
```http
GET /api/tags
```

Retrieves all available tags for content categorization.

**Response:**
```json
{
  "tags": [
    {
      "id": "tag_123",
      "name": "programming",
      "usage_count": 25
    },
    {
      "id": "tag_124",
      "name": "javascript",
      "usage_count": 15
    }
  ]
}
```

#### Create Tag
```http
POST /api/tags
```

Creates a new tag.

**Request Body:**
```json
{
  "name": "python"
}
```

### Usage Examples

#### Complete Course Creation Workflow

```javascript
class ContentManager {
    constructor(accessToken) {
        this.token = accessToken;
        this.baseURL = 'https://api.example.com/api';
    }

    async createCourse(courseData) {
        const response = await fetch(`${this.baseURL}/courses`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(courseData)
        });
        return await response.json();
    }

    async addSection(courseId, sectionData) {
        const response = await fetch(`${this.baseURL}/courses/${courseId}/sections`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sectionData)
        });
        return await response.json();
    }

    async addMaterial(sectionId, materialData) {
        const response = await fetch(`${this.baseURL}/sections/${sectionId}/materials`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(materialData)
        });
        return await response.json();
    }

    async uploadVideo(materialId, videoFile) {
        // Get presigned URL
        const presignResponse = await fetch(`${this.baseURL}/materials/${materialId}/upload/presign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_type: videoFile.type,
                file_size: videoFile.size,
                file_name: videoFile.name
            })
        });

        const { upload_url } = await presignResponse.json();

        // Upload to cloud storage
        await fetch(upload_url, {
            method: 'PUT',
            body: videoFile,
            headers: {
                'Content-Type': videoFile.type
            }
        });
    }
}

// Usage example
const contentManager = new ContentManager('your-access-token');

async function createFullCourse() {
    // Create course
    const course = await contentManager.createCourse({
        title: 'JavaScript Fundamentals',
        description: 'Learn JavaScript from scratch',
        status: 'draft'
    });

    // Add section
    const section = await contentManager.addSection(course.id, {
        title: 'Variables and Functions',
        sequence: 1
    });

    // Add video material
    const material = await contentManager.addMaterial(section.id, {
        type: 'video',
        title: 'Introduction to Variables',
        status: 'draft'
    });

    // Upload video file
    const videoFile = document.getElementById('video-input').files[0];
    await contentManager.uploadVideo(material.id, videoFile);

    console.log('Course created successfully!');
}
```

---

## Profile Service (Profile API)

**Version**: 0.1.0  
**Base URL**: `/api/profile`  
**Technology**: Python FastAPI

### Overview
The Profile service manages user profile information including personal details, contact information, and avatar management. It provides secure profile updates and avatar upload functionality.

### Authentication
All endpoints require a valid JWT access token from the Auth service.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Data Model

#### Profile Schema
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "nickname": "johnny",
  "birth_date": "1990-05-15",
  "gender": "male",
  "country": "United States",
  "city": "New York",
  "company": "Tech Corp",
  "position": "Software Engineer",
  "experience_id": 3,
  "avatar_url": "https://cdn.example.com/avatars/user123.jpg",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Field Descriptions:**
- `user_id` (UUID, required): Unique user identifier
- `first_name` (string, required): User's first name (max 100 chars)
- `nickname` (string, optional): Display nickname (max 50 chars)
- `birth_date` (date, optional): Date of birth in YYYY-MM-DD format
- `gender` (enum, optional): One of "male", "female", "other"
- `country` (string, optional): Country name (max 100 chars)
- `city` (string, optional): City name (max 100 chars)
- `company` (string, optional): Company name (max 150 chars)
- `position` (string, optional): Job position (max 150 chars)
- `experience_id` (integer, optional): Years of experience category
- `avatar_url` (string, optional): URL to user's avatar image
- `updated_at` (datetime, required): Last update timestamp

### Public Endpoints

#### Get Profile
```http
GET /api/profile
```

Retrieves the current user's profile information.

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "nickname": "johnny",
  "birth_date": "1990-05-15",
  "gender": "male",
  "country": "United States",
  "city": "New York",
  "company": "Tech Corp",
  "position": "Software Engineer",
  "experience_id": 3,
  "avatar_url": "https://cdn.example.com/avatars/user123.jpg",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Profile retrieved successfully
- `401 Unauthorized` - Invalid or missing access token
- `404 Not Found` - Profile not found for user

**Example:**
```bash
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  "https://api.example.com/api/profile"
```

#### Update Profile
```http
PUT /api/profile
```

Updates the current user's profile information. Only provided fields will be updated.

**Request Body:**
```json
{
  "first_name": "John",
  "nickname": "johnny_dev",
  "birth_date": "1990-05-15",
  "gender": "male",
  "country": "United States",
  "city": "San Francisco",
  "company": "New Tech Corp",
  "position": "Senior Software Engineer",
  "experience_id": 5
}
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "first_name": "John",
  "nickname": "johnny_dev",
  "birth_date": "1990-05-15",
  "gender": "male",
  "country": "United States",
  "city": "San Francisco",
  "company": "New Tech Corp",
  "position": "Senior Software Engineer",
  "experience_id": 5,
  "avatar_url": "https://cdn.example.com/avatars/user123.jpg",
  "updated_at": "2024-01-15T11:30:00Z"
}
```

**Status Codes:**
- `200 OK` - Profile updated successfully
- `400 Bad Request` - Invalid data format or validation errors
- `401 Unauthorized` - Invalid or missing access token

**Validation Rules:**
- `first_name`: Required, 1-100 characters
- `nickname`: Optional, 1-50 characters
- `birth_date`: Optional, valid date format (YYYY-MM-DD)
- `gender`: Optional, must be "male", "female", or "other"
- `country`: Optional, 1-100 characters
- `city`: Optional, 1-100 characters
- `company`: Optional, 1-150 characters
- `position`: Optional, 1-150 characters
- `experience_id`: Optional, positive integer

**Example:**
```bash
curl -X PUT "https://api.example.com/api/profile" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "city": "San Francisco",
    "position": "Senior Software Engineer"
  }'
```

### Avatar Management

#### Request Avatar Upload URL
```http
POST /api/profile/avatar/presign
```

Generates a presigned URL for uploading a new avatar image directly to cloud storage.

**Request Body:**
```json
{
  "content_type": "image/jpeg",
  "size": 204800
}
```

**Parameters:**
- `content_type` (string, required): MIME type of the image
- `size` (integer, required): File size in bytes

**Supported Content Types:**
- `image/jpeg`
- `image/png`
- `image/webp`

**Size Limits:**
- Minimum: 1 KB
- Maximum: 5 MB

**Response:**
```json
{
  "upload_url": "https://storage.example.com/avatars/presigned-upload-url",
  "avatar_url": "https://cdn.example.com/avatars/user123_new.jpg"
}
```

**Status Codes:**
- `200 OK` - Upload URL generated successfully
- `400 Bad Request` - Invalid content type or file size
- `401 Unauthorized` - Invalid or missing access token

#### Avatar Upload Process

1. **Request presigned URL** with image details
2. **Upload image directly** to cloud storage using the presigned URL
3. **Profile avatar_url** is automatically updated upon successful upload

**Complete Avatar Upload Example:**
```javascript
async function uploadAvatar(accessToken, imageFile) {
    try {
        // Step 1: Request presigned URL
        const presignResponse = await fetch('https://api.example.com/api/profile/avatar/presign', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_type: imageFile.type,
                size: imageFile.size
            })
        });

        if (!presignResponse.ok) {
            throw new Error('Failed to get upload URL');
        }

        const { upload_url, avatar_url } = await presignResponse.json();

        // Step 2: Upload image to cloud storage
        const uploadResponse = await fetch(upload_url, {
            method: 'PUT',
            body: imageFile,
            headers: {
                'Content-Type': imageFile.type
            }
        });

        if (!uploadResponse.ok) {
            throw new Error('Failed to upload image');
        }

        console.log('Avatar uploaded successfully!');
        console.log('New avatar URL:', avatar_url);
        
        return avatar_url;
    } catch (error) {
        console.error('Avatar upload failed:', error);
        throw error;
    }
}

// Usage
const fileInput = document.getElementById('avatar-input');
const imageFile = fileInput.files[0];
const newAvatarUrl = await uploadAvatar('your-access-token', imageFile);
```

### Usage Examples

#### Complete Profile Management

```javascript
class ProfileManager {
    constructor(accessToken) {
        this.token = accessToken;
        this.baseURL = 'https://api.example.com/api/profile';
    }

    async getProfile() {
        const response = await fetch(this.baseURL, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch profile');
        }

        return await response.json();
    }

    async updateProfile(profileData) {
        const response = await fetch(this.baseURL, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(profileData)
        });

        if (!response.ok) {
            throw new Error('Failed to update profile');
        }

        return await response.json();
    }

    async uploadAvatar(imageFile) {
        // Validate file
        if (!imageFile.type.startsWith('image/')) {
            throw new Error('File must be an image');
        }

        if (imageFile.size > 5 * 1024 * 1024) { // 5MB
            throw new Error('File size must be less than 5MB');
        }

        // Get presigned URL
        const presignResponse = await fetch(`${this.baseURL}/avatar/presign`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                content_type: imageFile.type,
                size: imageFile.size
            })
        });

        if (!presignResponse.ok) {
            throw new Error('Failed to get upload URL');
        }

        const { upload_url, avatar_url } = await presignResponse.json();

        // Upload to cloud storage
        const uploadResponse = await fetch(upload_url, {
            method: 'PUT',
            body: imageFile,
            headers: {
                'Content-Type': imageFile.type
            }
        });

        if (!uploadResponse.ok) {
            throw new Error('Failed to upload avatar');
        }

        return avatar_url;
    }

    // Utility method to update profile with avatar
    async updateProfileWithAvatar(profileData, avatarFile) {
        let updatedProfile = profileData;

        // Upload avatar if provided
        if (avatarFile) {
            const avatarUrl = await this.uploadAvatar(avatarFile);
            updatedProfile = { ...profileData, avatar_url: avatarUrl };
        }

        return await this.updateProfile(updatedProfile);
    }
}

// Usage example
const profileManager = new ProfileManager('your-access-token');

// Get current profile
const currentProfile = await profileManager.getProfile();
console.log('Current profile:', currentProfile);

// Update profile information
const updatedProfile = await profileManager.updateProfile({
    first_name: 'John',
    nickname: 'johnny_dev',
    city: 'San Francisco',
    position: 'Senior Developer'
});

// Upload new avatar
const avatarFile = document.getElementById('avatar-input').files[0];
const newAvatarUrl = await profileManager.uploadAvatar(avatarFile);

// Update profile with both data and avatar
const completeUpdate = await profileManager.updateProfileWithAvatar({
    company: 'New Company',
    position: 'Tech Lead'
}, avatarFile);
```

#### Form Integration Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Profile Management</title>
</head>
<body>
    <form id="profile-form">
        <div>
            <label>First Name:</label>
            <input type="text" name="first_name" required maxlength="100">
        </div>
        
        <div>
            <label>Nickname:</label>
            <input type="text" name="nickname" maxlength="50">
        </div>
        
        <div>
            <label>Birth Date:</label>
            <input type="date" name="birth_date">
        </div>
        
        <div>
            <label>Gender:</label>
            <select name="gender">
                <option value="">Select...</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
            </select>
        </div>
        
        <div>
            <label>Country:</label>
            <input type="text" name="country" maxlength="100">
        </div>
        
        <div>
            <label>City:</label>
            <input type="text" name="city" maxlength="100">
        </div>
        
        <div>
            <label>Company:</label>
            <input type="text" name="company" maxlength="150">
        </div>
        
        <div>
            <label>Position:</label>
            <input type="text" name="position" maxlength="150">
        </div>
        
        <div>
            <label>Avatar:</label>
            <input type="file" id="avatar-input" accept="image/*">
        </div>
        
        <button type="submit">Update Profile</button>
    </form>

    <script>
        document.getElementById('profile-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const profileData = Object.fromEntries(formData.entries());
            
            // Remove empty values
            Object.keys(profileData).forEach(key => {
                if (profileData[key] === '') {
                    delete profileData[key];
                }
            });
            
            const avatarFile = document.getElementById('avatar-input').files[0];
            
            try {
                const profileManager = new ProfileManager('your-access-token');
                
                if (avatarFile) {
                    await profileManager.updateProfileWithAvatar(profileData, avatarFile);
                } else {
                    await profileManager.updateProfile(profileData);
                }
                
                alert('Profile updated successfully!');
            } catch (error) {
                alert('Error updating profile: ' + error.message);
            }
        });
    </script>
</body>
</html>
```

### Experience Levels

The `experience_id` field maps to predefined experience levels:

| ID | Level | Description |
|----|-------|-------------|
| 1 | Entry Level | 0-1 years |
| 2 | Junior | 1-3 years |
| 3 | Mid-Level | 3-5 years |
| 4 | Senior | 5-8 years |
| 5 | Expert | 8+ years |

---

## Notifications Service (Notifications API)

**Version**: 0.2.0  
**Base URL**: `/api`  
**Technology**: Python FastAPI

### Overview
The Notifications service provides multi-channel notification delivery supporting email, SMS, and push notifications. It features template-based messaging, delivery queuing, and user subscription management.

### Authentication
Most endpoints require a valid JWT access token from the Auth service.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Supported Channels

- **Email**: HTML and text email notifications
- **SMS**: Text message notifications
- **Push**: Mobile and web push notifications

### Public Endpoints

#### Send Notification
```http
POST /api/notify/send
```

Queues a notification for delivery through the specified channel.

**Request Body:**
```json
{
  "channel": "email",
  "recipient": "user@example.com",
  "template": "welcome_email",
  "data": {
    "user_name": "John Doe",
    "activation_link": "https://app.example.com/activate/token123"
  },
  "idempotency_key": "unique-request-id-123"
}
```

**Parameters:**
- `channel` (string, required): Delivery channel - "email", "sms", or "push"
- `recipient` (string, required): Recipient identifier (email, phone, or device token)
- `template` (string, required): Template name to use for the notification
- `data` (object, optional): Template variables for personalization
- `idempotency_key` (string, optional): Unique key to prevent duplicate sends

**Response:**
- `202 Accepted` - Notification queued for delivery
- `400 Bad Request` - Invalid request format or parameters
- `404 Not Found` - Template not found
- `429 Too Many Requests` - Rate limit exceeded

**Example:**
```bash
curl -X POST "https://api.example.com/api/notify/send" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "template": "password_reset",
    "data": {
      "user_name": "John Doe",
      "reset_link": "https://app.example.com/reset/abc123"
    }
  }'
```

#### Preview Notification
```http
POST /api/notify/preview
```

Renders a notification template without sending it. Useful for testing and previewing templates.

**Request Body:**
```json
{
  "channel": "email",
  "template": "welcome_email",
  "data": {
    "user_name": "John Doe",
    "activation_link": "https://app.example.com/activate/token123"
  }
}
```

**Response:**
```json
{
  "subject": "Welcome to Our Platform!",
  "content": "<html><body><h1>Welcome John Doe!</h1><p>Click <a href='https://app.example.com/activate/token123'>here</a> to activate your account.</p></body></html>",
  "text_content": "Welcome John Doe! Click here to activate your account: https://app.example.com/activate/token123"
}
```

### User Subscription Management

#### Get User Subscriptions
```http
GET /api/subscriptions
```

Retrieves the current user's notification preferences and subscriptions.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "subscriptions": {
    "email": {
      "marketing": true,
      "product_updates": true,
      "security_alerts": true,
      "course_notifications": false
    },
    "sms": {
      "security_alerts": true,
      "urgent_notifications": true
    },
    "push": {
      "chat_messages": true,
      "course_reminders": true,
      "system_notifications": false
    }
  },
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Update User Subscriptions
```http
PUT /api/subscriptions
```

Updates the current user's notification preferences.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "email": {
    "marketing": false,
    "product_updates": true,
    "security_alerts": true,
    "course_notifications": true
  },
  "sms": {
    "security_alerts": true,
    "urgent_notifications": false
  },
  "push": {
    "chat_messages": true,
    "course_reminders": false,
    "system_notifications": true
  }
}
```

**Response:**
```json
{
  "subscriptions": {
    "email": {
      "marketing": false,
      "product_updates": true,
      "security_alerts": true,
      "course_notifications": true
    },
    "sms": {
      "security_alerts": true,
      "urgent_notifications": false
    },
    "push": {
      "chat_messages": true,
      "course_reminders": false,
      "system_notifications": true
    }
  },
  "updated_at": "2024-01-15T11:30:00Z"
}
```

### Available Templates

#### Authentication Templates
- `welcome_email` - Welcome message for new users
- `email_verification` - Email address verification
- `password_reset` - Password reset instructions
- `login_alert` - Suspicious login attempt notification
- `account_locked` - Account locked notification

#### Course Templates
- `course_enrolled` - Course enrollment confirmation
- `course_completed` - Course completion certificate
- `lesson_reminder` - Upcoming lesson reminder
- `assignment_due` - Assignment due date reminder

#### System Templates
- `maintenance_notice` - System maintenance notification
- `feature_announcement` - New feature announcement
- `security_update` - Security-related updates

### Channel-Specific Configuration

#### Email Configuration
```json
{
  "channel": "email",
  "recipient": "user@example.com",
  "template": "welcome_email",
  "data": {
    "user_name": "John Doe",
    "activation_link": "https://app.example.com/activate/token123",
    "support_email": "support@example.com"
  }
}
```

#### SMS Configuration
```json
{
  "channel": "sms",
  "recipient": "+1234567890",
  "template": "verification_code",
  "data": {
    "code": "123456",
    "expires_in": "5 minutes"
  }
}
```

#### Push Notification Configuration
```json
{
  "channel": "push",
  "recipient": "device_token_or_user_id",
  "template": "chat_message",
  "data": {
    "sender_name": "Alice",
    "message_preview": "Hey, how are you doing?",
    "chat_id": "chat_123"
  }
}
```

### Usage Examples

#### Notification Service Client

```javascript
class NotificationService {
    constructor(baseURL = 'https://api.example.com/api') {
        this.baseURL = baseURL;
    }

    async sendNotification(notificationData) {
        const response = await fetch(`${this.baseURL}/notify/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(notificationData)
        });

        if (!response.ok) {
            throw new Error(`Failed to send notification: ${response.statusText}`);
        }

        return response.status === 202;
    }

    async previewNotification(previewData) {
        const response = await fetch(`${this.baseURL}/notify/preview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(previewData)
        });

        if (!response.ok) {
            throw new Error(`Failed to preview notification: ${response.statusText}`);
        }

        return await response.json();
    }

    async getUserSubscriptions(accessToken) {
        const response = await fetch(`${this.baseURL}/subscriptions`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get subscriptions: ${response.statusText}`);
        }

        return await response.json();
    }

    async updateUserSubscriptions(accessToken, subscriptions) {
        const response = await fetch(`${this.baseURL}/subscriptions`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subscriptions)
        });

        if (!response.ok) {
            throw new Error(`Failed to update subscriptions: ${response.statusText}`);
        }

        return await response.json();
    }

    // Helper methods for common notifications
    async sendWelcomeEmail(email, userData) {
        return await this.sendNotification({
            channel: 'email',
            recipient: email,
            template: 'welcome_email',
            data: userData
        });
    }

    async sendPasswordReset(email, resetData) {
        return await this.sendNotification({
            channel: 'email',
            recipient: email,
            template: 'password_reset',
            data: resetData,
            idempotency_key: `password_reset_${email}_${Date.now()}`
        });
    }

    async sendSMSVerification(phone, code) {
        return await this.sendNotification({
            channel: 'sms',
            recipient: phone,
            template: 'verification_code',
            data: { code, expires_in: '5 minutes' }
        });
    }

    async sendPushNotification(userId, messageData) {
        return await this.sendNotification({
            channel: 'push',
            recipient: userId,
            template: 'chat_message',
            data: messageData
        });
    }
}

// Usage examples
const notificationService = new NotificationService();

// Send welcome email
await notificationService.sendWelcomeEmail('user@example.com', {
    user_name: 'John Doe',
    activation_link: 'https://app.example.com/activate/token123'
});

// Send password reset
await notificationService.sendPasswordReset('user@example.com', {
    user_name: 'John Doe',
    reset_link: 'https://app.example.com/reset/abc123',
    expires_in: '1 hour'
});

// Preview notification
const preview = await notificationService.previewNotification({
    channel: 'email',
    template: 'welcome_email',
    data: { user_name: 'John Doe' }
});
console.log('Email preview:', preview);
```

#### Subscription Management Component

```javascript
class SubscriptionManager {
    constructor(accessToken) {
        this.token = accessToken;
        this.notificationService = new NotificationService();
    }

    async loadSubscriptions() {
        try {
            const response = await this.notificationService.getUserSubscriptions(this.token);
            return response.subscriptions;
        } catch (error) {
            console.error('Failed to load subscriptions:', error);
            throw error;
        }
    }

    async updateSubscriptions(subscriptions) {
        try {
            const response = await this.notificationService.updateUserSubscriptions(
                this.token, 
                subscriptions
            );
            return response.subscriptions;
        } catch (error) {
            console.error('Failed to update subscriptions:', error);
            throw error;
        }
    }

    // Helper method to toggle a specific subscription
    async toggleSubscription(channel, type, enabled) {
        const currentSubscriptions = await this.loadSubscriptions();
        
        const updatedSubscriptions = {
            ...currentSubscriptions,
            [channel]: {
                ...currentSubscriptions[channel],
                [type]: enabled
            }
        };

        return await this.updateSubscriptions(updatedSubscriptions);
    }
}

// Usage
const subscriptionManager = new SubscriptionManager('user-access-token');

// Load current subscriptions
const subscriptions = await subscriptionManager.loadSubscriptions();

// Toggle email marketing
await subscriptionManager.toggleSubscription('email', 'marketing', false);

// Update multiple subscriptions
await subscriptionManager.updateSubscriptions({
    email: {
        marketing: false,
        product_updates: true,
        security_alerts: true
    },
    push: {
        chat_messages: true,
        course_reminders: false
    }
});
```

### Error Handling

The service returns consistent error responses:

```json
{
  "error": {
    "code": "TEMPLATE_NOT_FOUND",
    "message": "The specified template 'invalid_template' was not found",
    "details": {
      "template": "invalid_template",
      "available_templates": ["welcome_email", "password_reset"]
    }
  }
}
```

**Common Error Codes:**
- `INVALID_CHANNEL` - Unsupported notification channel
- `TEMPLATE_NOT_FOUND` - Template does not exist
- `INVALID_RECIPIENT` - Invalid recipient format
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `DELIVERY_FAILED` - Notification delivery failed

### Best Practices

1. **Use Idempotency Keys**: Prevent duplicate notifications by using unique idempotency keys
2. **Template Data Validation**: Ensure all required template variables are provided
3. **Graceful Degradation**: Handle notification failures gracefully in your application
4. **Respect User Preferences**: Check user subscriptions before sending notifications
5. **Monitor Delivery**: Implement webhooks or polling to monitor delivery status

---

## Analytics Service (Analytics API)

**Version**: 0.1.0  
**Base URL**: `/api/analytics`  
**Technology**: Python FastAPI

### Overview
The Analytics service provides event tracking, data ingestion, and reporting capabilities. It collects user behavior data, processes events in batches, and generates insights through various reporting endpoints.

### Authentication
All endpoints require a valid JWT access token from the Auth service.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Data Model

#### Event Schema
```json
{
  "ts": "2024-01-15T10:30:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "page_view",
  "src": "web_app",
  "payload": {
    "page": "/dashboard",
    "referrer": "https://google.com",
    "user_agent": "Mozilla/5.0...",
    "session_id": "session_123"
  }
}
```

**Field Descriptions:**
- `ts` (datetime, required): Event timestamp in ISO 8601 format
- `user_id` (UUID, required): User who triggered the event
- `type` (string, required): Event type identifier
- `src` (string, optional): Event source (web_app, mobile_app, api, etc.)
- `payload` (object, required): Event-specific data and context

### Public Endpoints

#### Ingest Events
```http
POST /api/analytics/ingest
```

Ingests a batch of events for processing and storage.

**Request Body:**
```json
[
  {
    "ts": "2024-01-15T10:30:00Z",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "page_view",
    "src": "web_app",
    "payload": {
      "page": "/dashboard",
      "referrer": "https://google.com"
    }
  },
  {
    "ts": "2024-01-15T10:31:00Z",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "button_click",
    "src": "web_app",
    "payload": {
      "button_id": "start_course",
      "course_id": "course_123"
    }
  }
]
```

**Response:**
```json
{
  "ingested": 2
}
```

**Status Codes:**
- `200 OK` - Events ingested successfully
- `400 Bad Request` - Invalid event format
- `413 Payload Too Large` - Batch size exceeds limit (max 1000 events)
- `429 Too Many Requests` - Rate limit exceeded

**Batch Limits:**
- Maximum 1000 events per batch
- Maximum 10 MB payload size
- Maximum 100 requests per minute per user

**Example:**
```bash
curl -X POST "https://api.example.com/api/analytics/ingest" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "ts": "2024-01-15T10:30:00Z",
      "user_id": "123e4567-e89b-12d3-a456-426614174000",
      "type": "course_started",
      "src": "web_app",
      "payload": {
        "course_id": "course_123",
        "course_title": "JavaScript Fundamentals"
      }
    }
  ]'
```

#### Get Dashboard Metrics
```http
GET /api/analytics/dashboard
```

Retrieves key metrics and KPIs for the analytics dashboard.

**Response:**
```json
{
  "overview": {
    "total_users": 1250,
    "active_users_today": 89,
    "active_users_week": 456,
    "active_users_month": 1100
  },
  "engagement": {
    "avg_session_duration": 1847,
    "page_views_today": 2340,
    "bounce_rate": 0.23
  },
  "content": {
    "courses_completed_today": 15,
    "lessons_watched_today": 234,
    "total_watch_time_minutes": 12450
  },
  "top_pages": [
    {
      "page": "/dashboard",
      "views": 1250,
      "unique_visitors": 890
    },
    {
      "page": "/courses",
      "views": 980,
      "unique_visitors": 750
    }
  ],
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Get Daily Active Users
```http
GET /api/analytics/reports/dau
```

Retrieves the current daily active users count.

**Response:**
```json
{
  "dau": 89,
  "date": "2024-01-15",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Export Events
```http
GET /api/analytics/reports/events
```

Exports event data in CSV or Excel format for analysis.

**Parameters:**
- `format` (query, required): Export format - "csv" or "xlsx"
- `start_date` (query, optional): Start date filter (YYYY-MM-DD)
- `end_date` (query, optional): End date filter (YYYY-MM-DD)
- `event_type` (query, optional): Filter by event type
- `user_id` (query, optional): Filter by specific user

**Response:**
- `200 OK` - Returns file stream in requested format
- `400 Bad Request` - Invalid parameters

**Example:**
```bash
# Export as CSV
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  "https://api.example.com/api/analytics/reports/events?format=csv&start_date=2024-01-01&end_date=2024-01-15" \
  --output events.csv

# Export as Excel
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  "https://api.example.com/api/analytics/reports/events?format=xlsx&event_type=course_completed" \
  --output course_completions.xlsx
```

### Common Event Types

#### User Events
- `user_registered` - New user registration
- `user_login` - User login
- `user_logout` - User logout
- `profile_updated` - Profile information changed

#### Navigation Events
- `page_view` - Page or screen viewed
- `button_click` - Button or link clicked
- `form_submit` - Form submitted
- `search_performed` - Search query executed

#### Course Events
- `course_viewed` - Course details page viewed
- `course_enrolled` - User enrolled in course
- `course_started` - User started course content
- `course_completed` - User completed entire course
- `lesson_started` - Individual lesson started
- `lesson_completed` - Individual lesson completed
- `video_played` - Video content played
- `video_paused` - Video content paused
- `video_completed` - Video watched to completion

#### Engagement Events
- `chat_message_sent` - Message sent in chat
- `file_downloaded` - File or resource downloaded
- `bookmark_added` - Content bookmarked
- `rating_submitted` - Rating or review submitted

### Usage Examples

#### Analytics Client

```javascript
class AnalyticsClient {
    constructor(accessToken) {
        this.token = accessToken;
        this.baseURL = 'https://api.example.com/api/analytics';
        this.eventQueue = [];
        this.batchSize = 50;
        this.flushInterval = 30000; // 30 seconds
        
        // Auto-flush events periodically
        setInterval(() => this.flush(), this.flushInterval);
    }

    // Track a single event
    track(eventType, payload = {}, source = 'web_app') {
        const event = {
            ts: new Date().toISOString(),
            user_id: this.getCurrentUserId(),
            type: eventType,
            src: source,
            payload: payload
        };

        this.eventQueue.push(event);

        // Flush if batch size reached
        if (this.eventQueue.length >= this.batchSize) {
            this.flush();
        }
    }

    // Send queued events to the server
    async flush() {
        if (this.eventQueue.length === 0) return;

        const events = [...this.eventQueue];
        this.eventQueue = [];

        try {
            const response = await fetch(`${this.baseURL}/ingest`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(events)
            });

            if (!response.ok) {
                // Re-queue events on failure
                this.eventQueue.unshift(...events);
                throw new Error(`Analytics ingestion failed: ${response.statusText}`);
            }

            const result = await response.json();
            console.log(`Analytics: ${result.ingested} events ingested`);
        } catch (error) {
            console.error('Analytics flush failed:', error);
            // Re-queue events for retry
            this.eventQueue.unshift(...events);
        }
    }

    // Get dashboard metrics
    async getDashboard() {
        const response = await fetch(`${this.baseURL}/dashboard`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get dashboard: ${response.statusText}`);
        }

        return await response.json();
    }

    // Get daily active users
    async getDAU() {
        const response = await fetch(`${this.baseURL}/reports/dau`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to get DAU: ${response.statusText}`);
        }

        return await response.json();
    }

    // Export events
    async exportEvents(format = 'csv', filters = {}) {
        const params = new URLSearchParams({ format, ...filters });
        
        const response = await fetch(`${this.baseURL}/reports/events?${params}`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to export events: ${response.statusText}`);
        }

        return response.blob();
    }

    // Helper method to get current user ID (implement based on your auth system)
    getCurrentUserId() {
        // This should return the current user's ID from your authentication system
        return localStorage.getItem('user_id') || 'anonymous';
    }

    // Convenience methods for common events
    trackPageView(page, referrer = null) {
        this.track('page_view', {
            page,
            referrer,
            user_agent: navigator.userAgent,
            timestamp: Date.now()
        });
    }

    trackButtonClick(buttonId, context = {}) {
        this.track('button_click', {
            button_id: buttonId,
            ...context
        });
    }

    trackCourseEvent(eventType, courseId, additionalData = {}) {
        this.track(eventType, {
            course_id: courseId,
            ...additionalData
        });
    }

    trackVideoEvent(eventType, videoId, currentTime = 0, duration = 0) {
        this.track(eventType, {
            video_id: videoId,
            current_time: currentTime,
            duration: duration,
            progress: duration > 0 ? currentTime / duration : 0
        });
    }
}

// Usage examples
const analytics = new AnalyticsClient('user-access-token');

// Track page views
analytics.trackPageView('/dashboard', 'https://google.com');

// Track user interactions
analytics.trackButtonClick('start_course_btn', {
    course_id: 'course_123',
    course_title: 'JavaScript Fundamentals'
});

// Track course events
analytics.trackCourseEvent('course_started', 'course_123', {
    course_title: 'JavaScript Fundamentals',
    section_id: 'section_1'
});

// Track video events
analytics.trackVideoEvent('video_played', 'video_456', 0, 300);
analytics.trackVideoEvent('video_completed', 'video_456', 300, 300);

// Get dashboard data
const dashboard = await analytics.getDashboard();
console.log('Dashboard metrics:', dashboard);
```

#### React Hook for Analytics

```javascript
import { useEffect, useRef } from 'react';

export function useAnalytics(accessToken) {
    const analyticsRef = useRef(null);

    useEffect(() => {
        if (accessToken && !analyticsRef.current) {
            analyticsRef.current = new AnalyticsClient(accessToken);
        }
    }, [accessToken]);

    const track = (eventType, payload, source) => {
        if (analyticsRef.current) {
            analyticsRef.current.track(eventType, payload, source);
        }
    };

    const trackPageView = (page, referrer) => {
        if (analyticsRef.current) {
            analyticsRef.current.trackPageView(page, referrer);
        }
    };

    const trackButtonClick = (buttonId, context) => {
        if (analyticsRef.current) {
            analyticsRef.current.trackButtonClick(buttonId, context);
        }
    };

    return {
        track,
        trackPageView,
        trackButtonClick,
        analytics: analyticsRef.current
    };
}

// Usage in React component
function CoursePlayer({ courseId, accessToken }) {
    const { track, trackButtonClick } = useAnalytics(accessToken);

    const handlePlayVideo = (videoId) => {
        track('video_played', {
            video_id: videoId,
            course_id: courseId
        });
    };

    const handleCompleteLesson = (lessonId) => {
        trackButtonClick('complete_lesson', {
            lesson_id: lessonId,
            course_id: courseId
        });
    };

    return (
        <div>
            <button onClick={() => handlePlayVideo('video_123')}>
                Play Video
            </button>
            <button onClick={() => handleCompleteLesson('lesson_456')}>
                Mark Complete
            </button>
        </div>
    );
}
```

#### Analytics Dashboard Component

```javascript
function AnalyticsDashboard({ accessToken }) {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const analytics = new AnalyticsClient(accessToken);

    useEffect(() => {
        loadDashboard();
    }, []);

    const loadDashboard = async () => {
        try {
            setLoading(true);
            const data = await analytics.getDashboard();
            setDashboardData(data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const exportData = async (format) => {
        try {
            const blob = await analytics.exportEvents(format);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics_export.${format}`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Export failed:', error);
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="analytics-dashboard">
            <h1>Analytics Dashboard</h1>
            
            <div className="metrics-grid">
                <div className="metric-card">
                    <h3>Total Users</h3>
                    <p>{dashboardData.overview.total_users}</p>
                </div>
                
                <div className="metric-card">
                    <h3>Daily Active Users</h3>
                    <p>{dashboardData.overview.active_users_today}</p>
                </div>
                
                <div className="metric-card">
                    <h3>Avg Session Duration</h3>
                    <p>{Math.round(dashboardData.engagement.avg_session_duration / 60)} min</p>
                </div>
                
                <div className="metric-card">
                    <h3>Courses Completed Today</h3>
                    <p>{dashboardData.content.courses_completed_today}</p>
                </div>
            </div>

            <div className="export-section">
                <h3>Export Data</h3>
                <button onClick={() => exportData('csv')}>
                    Export as CSV
                </button>
                <button onClick={() => exportData('xlsx')}>
                    Export as Excel
                </button>
            </div>
        </div>
    );
}
```

### Best Practices

1. **Batch Events**: Collect events locally and send in batches for better performance
2. **Handle Failures**: Implement retry logic for failed event ingestion
3. **Privacy Compliance**: Ensure event data complies with privacy regulations (GDPR, CCPA)
4. **Data Quality**: Validate event data before sending to maintain data integrity
5. **Performance**: Avoid blocking UI with analytics calls - use async operations
6. **Sampling**: Consider sampling high-volume events to manage costs and performance

---

## Content Worker Service

**Version**: N/A (Background Service)  
**Technology**: Python

### Overview
The Content Worker service is a background processing service that handles asynchronous content-related tasks such as video processing, thumbnail generation, content indexing, and media optimization.

### Key Responsibilities

1. **Video Processing**: Transcoding videos to multiple formats and resolutions
2. **Thumbnail Generation**: Creating preview images for video content
3. **Content Indexing**: Building search indexes for course materials
4. **Media Optimization**: Compressing and optimizing uploaded media files
5. **Notification Triggering**: Sending notifications when processing is complete

### Architecture

The service operates as a background worker that:
- Consumes messages from a queue (Redis/RabbitMQ)
- Processes content asynchronously
- Updates content status in the database
- Triggers notifications upon completion

### Integration Points

The Content Worker integrates with:
- **Content Service**: Receives processing tasks and updates status
- **Notifications Service**: Sends completion notifications
- **Cloud Storage**: Accesses and stores processed media files

### Typical Workflow

1. User uploads content via Content Service
2. Content Service queues processing task
3. Content Worker picks up task from queue
4. Worker processes content (transcode, optimize, etc.)
5. Worker updates content status to "ready"
6. Worker triggers notification to user

---

## Error Handling and Status Codes

### Standard HTTP Status Codes

All services follow consistent HTTP status code conventions:

#### Success Codes
- `200 OK` - Request successful, response body contains data
- `201 Created` - Resource created successfully
- `202 Accepted` - Request accepted for processing (async operations)
- `204 No Content` - Request successful, no response body

#### Client Error Codes
- `400 Bad Request` - Invalid request format or parameters
- `401 Unauthorized` - Authentication required or invalid
- `403 Forbidden` - Authenticated but not authorized for this resource
- `404 Not Found` - Resource does not exist
- `409 Conflict` - Resource conflict (e.g., duplicate email)
- `413 Payload Too Large` - Request body too large
- `422 Unprocessable Entity` - Valid format but semantic errors
- `429 Too Many Requests` - Rate limit exceeded

#### Server Error Codes
- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - Service unavailable
- `503 Service Unavailable` - Temporary service outage
- `504 Gateway Timeout` - Request timeout

### Error Response Format

All services return errors in a consistent format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      "field": "Additional context or field-specific errors"
    },
    "request_id": "req_123456789"
  }
}
```

### Common Error Codes

#### Authentication Errors
- `INVALID_TOKEN` - JWT token is malformed or invalid
- `TOKEN_EXPIRED` - JWT token has expired
- `INSUFFICIENT_PERMISSIONS` - User lacks required permissions

#### Validation Errors
- `INVALID_REQUEST` - Request format is invalid
- `MISSING_REQUIRED_FIELD` - Required field is missing
- `INVALID_FIELD_FORMAT` - Field format is incorrect
- `VALUE_OUT_OF_RANGE` - Field value exceeds allowed range

#### Resource Errors
- `RESOURCE_NOT_FOUND` - Requested resource does not exist
- `RESOURCE_ALREADY_EXISTS` - Resource with same identifier exists
- `RESOURCE_LOCKED` - Resource is locked for editing

#### Rate Limiting
- `RATE_LIMIT_EXCEEDED` - Too many requests from client
- `QUOTA_EXCEEDED` - Usage quota exceeded

---

## Authentication and Authorization

### JWT Token Structure

All services use JWT (JSON Web Tokens) for authentication. Tokens contain:

```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "roles": ["user", "student"],
  "permissions": ["read:profile", "write:profile"],
  "exp": 1642694400,
  "iat": 1642608000,
  "iss": "auth-service"
}
```

### Authorization Headers

Include the access token in all API requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Permission Model

The system uses role-based access control (RBAC) with the following roles:

#### User Roles
- `user` - Basic authenticated user
- `student` - Enrolled student with course access
- `instructor` - Can create and manage courses
- `admin` - Full system access

#### Permissions
- `read:profile` - View profile information
- `write:profile` - Update profile information
- `read:courses` - View course content
- `write:courses` - Create/edit courses
- `manage:users` - User management (admin only)

---

## Rate Limiting

All services implement rate limiting to prevent abuse:

### Default Limits
- **Authentication endpoints**: 10 requests per minute per IP
- **API endpoints**: 1000 requests per hour per user
- **File uploads**: 10 uploads per hour per user
- **Analytics ingestion**: 100 batches per minute per user

### Rate Limit Headers

Responses include rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "limit": 1000,
      "window": "1 hour",
      "reset_at": "2024-01-15T11:00:00Z"
    }
  }
}
```

---

## Development and Testing

### API Testing

#### Using cURL

```bash
# Set your access token
export ACCESS_TOKEN="your_access_token_here"

# Test auth endpoints
curl -X POST "https://api.example.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Test authenticated endpoints
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://api.example.com/api/profile"
```

#### Using JavaScript/Node.js

```javascript
// Test client
class APIClient {
    constructor(baseURL, accessToken) {
        this.baseURL = baseURL;
        this.token = accessToken;
    }

    async request(method, endpoint, data = null) {
        const url = `${this.baseURL}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(`API Error: ${responseData.error?.message || response.statusText}`);
        }

        return responseData;
    }

    // Auth methods
    async login(email, password) {
        return await this.request('POST', '/api/auth/login', { email, password });
    }

    // Profile methods
    async getProfile() {
        return await this.request('GET', '/api/profile');
    }

    async updateProfile(profileData) {
        return await this.request('PUT', '/api/profile', profileData);
    }

    // Course methods
    async getCourses() {
        return await this.request('GET', '/api/courses');
    }

    async createCourse(courseData) {
        return await this.request('POST', '/api/courses', courseData);
    }
}

// Usage
const client = new APIClient('https://api.example.com', 'your-access-token');

try {
    const profile = await client.getProfile();
    console.log('Profile:', profile);
} catch (error) {
    console.error('Error:', error.message);
}
```

### Environment Configuration

#### Development Environment
```bash
# API Base URLs
AUTH_API_URL=http://localhost:8001
CHAT_API_URL=http://localhost:8002
CONTENT_API_URL=http://localhost:8003
PROFILE_API_URL=http://localhost:8004
NOTIFICATIONS_API_URL=http://localhost:8005
ANALYTICS_API_URL=http://localhost:8006
```

#### Production Environment
```bash
# API Base URLs
AUTH_API_URL=https://auth.api.example.com
CHAT_API_URL=https://chat.api.example.com
CONTENT_API_URL=https://content.api.example.com
PROFILE_API_URL=https://profile.api.example.com
NOTIFICATIONS_API_URL=https://notifications.api.example.com
ANALYTICS_API_URL=https://analytics.api.example.com
```

---

## Conclusion

This comprehensive API documentation covers all public APIs, functions, and components in the microservices architecture. Each service is designed to be:

- **Independent**: Services can be developed, deployed, and scaled independently
- **Consistent**: All services follow the same patterns for authentication, error handling, and response formats
- **Scalable**: Services are designed to handle high load and can be horizontally scaled
- **Secure**: Comprehensive authentication and authorization mechanisms protect all endpoints
- **Observable**: Built-in metrics, logging, and analytics provide visibility into system behavior

### Quick Reference

| Service | Base URL | Primary Function |
|---------|----------|------------------|
| Auth | `/api/auth` | Authentication & authorization |
| Chat | `/api/chats` | Real-time messaging |
| Content | `/api` | Course & content management |
| Profile | `/api/profile` | User profile management |
| Notifications | `/api` | Multi-channel notifications |
| Analytics | `/api/analytics` | Event tracking & reporting |

### Getting Started

1. **Authentication**: Start by obtaining access tokens from the Auth service
2. **Profile Setup**: Create or update user profiles via the Profile service
3. **Content Access**: Browse and interact with courses via the Content service
4. **Real-time Features**: Connect to chat via WebSocket for live messaging
5. **Analytics**: Track user behavior and generate insights
6. **Notifications**: Set up notification preferences and delivery

For additional support or questions about the APIs, please refer to the individual service documentation or contact the development team.
