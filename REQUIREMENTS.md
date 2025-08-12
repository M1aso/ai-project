## 1. Introduction

**Project Goal:** Develop a corporate e-learning platform for managing and delivering online courses, featuring phone- and email-based authentication, a flexible role-based access control system, a content management module, notification services, an integrated chat system, and comprehensive analytics.

**Terms and Abbreviations:**

- **API** — HTTP RESTful services returning JSON.
- **MS** — Microservice.
- **JWT** — JSON Web Token.
- **TTL** — Time To Live (in seconds).
- **HPA** — Horizontal Pod Autoscaler.

---

## 2. Overall Architecture and Infrastructure

### 2.1. System Components

| Component            | Description                                                                                                  | Technologies / Notes                          |
| -------------------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| API Gateway          | Single entry point, routes requests to microservices, validates JWT, terminates SSL/TLS                      | Envoy or Nginx                                |
| Auth Service         | Registration, login, JWT access/refresh flow, password reset, CSRF protection                                | Python/Node.js + PostgreSQL                   |
| Profile Service      | User profile CRUD, social account linking (OAuth), profile change history                                    | Python + PostgreSQL                           |
| Content Service      | Course, section and material CRUD; integration with object storage and video transcoder                      | Go + PostgreSQL + MinIO/Yandex Object Storage |
| Notification Service | Notification templates, user subscription settings, queue management, integration with SMTP and Telegram API | Python + Redis + Celery + RabbitMQ            |
| Chat Service         | WebSocket server for personal/group chats, message and attachment storage                                    | Node.js + Redis + PostgreSQL                  |
| Analytics Service    | Metrics collection, dashboards, PDF/XLSX report generation                                                   | Python + Pandas + PostgreSQL + Celery         |
| Database             | Relational database in HA mode, replication, backups                                                         | Yandex Managed PostgreSQL                     |
| Object Storage       | Stores media files, avatars, and generated reports                                                           | Yandex Object Storage                         |
| Message Broker       | Task queues for video transcoding, notification dispatch, report generation                                  | RabbitMQ or Kafka                             |
| Monitoring & Logging | Metrics collection (Prometheus + Grafana), centralized logs (EFK stack)                                      |                                               |
| CI/CD                | Build, test, and deploy pipelines                                                                            | GitLab CI/CD                                  |

### 2.2. Deployment Environment

- **Kubernetes:** Yandex Managed Service for Kubernetes with namespaces `dev`, `staging`, `prod`.
- **Package Management:** Helm charts for each microservice.
- **Auto-scaling:** HPA based on CPU and memory usage.
- **Configuration & Secrets:** Managed via Kubernetes ConfigMaps and Secrets.

---

## 3. Authentication Module

### 3.1. Use Cases

| ID   | Use Case Description                                                                                                                                                |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| UC01 | **Phone Registration (RU):** User enters a Russian phone number (`+7...`), receives an SMS code, verifies it, provides email and password to complete registration. |
| UC02 | **Email Registration (non-RU):** User registers with email and password, receives a confirmation link via email (TTL 24h).                                          |
| UC03 | **Phone Login:** User enters phone number and SMS code to receive `access_token` (TTL 1h) and `refresh_token` (TTL 30d or 60d if "remember me").                    |
| UC04 | **Email Login:** User logs in with email and password, with optional "remember me" to extend `refresh_token` TTL.                                                   |
| UC05 | **Password Reset:** User requests reset via email, receives token (TTL 15m), sets a new password, and all existing sessions are invalidated.                        |
| UC06 | **Logout:** Invalidate the current `refresh_token`.                                                                                                                 |
| UC07 | **Brute-Force Protection:** Block SMS code verification after 5 failed attempts within 1 hour (`blocked_until` field).                                              |
| UC08 | **Phone Update:** User requests to change phone, verifies new number by SMS, replaces phone and invalidates sessions.                                               |
| UC09 | **Email Update:** User requests to change email, verifies via confirmation link, replaces email and invalidates sessions.                                           |

### 3.2. Database Schema (ERD)

```sql
-- users table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  login_type VARCHAR(10) NOT NULL CHECK (login_type IN ('phone','email')),
  phone VARCHAR(15) UNIQUE,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  is_active BOOLEAN DEFAULT FALSE,
  blocked_until TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- sms_codes table
CREATE TABLE sms_codes (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(15) NOT NULL,
  code CHAR(6) NOT NULL,
  sent_at TIMESTAMPTZ DEFAULT now(),
  attempts INT DEFAULT 0
);

-- refresh_tokens table
CREATE TABLE refresh_tokens (
  token CHAR(64) PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 3.3. REST API Endpoints

#### 3.3.1. POST `/api/auth/phone/send-code`

- **Description:** Send SMS code for phone-based registration or login.
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  { "phone": "+7XXXXXXXXXX" }
  ```
- **Validation & Rate Limits:**
  - E.164 format with `+7` prefix.
  - Max 1 request per phone per 30 seconds.
  - Max 5 requests per IP per hour.
- **Responses:**
  - `200 OK` — `{ "message": "Code sent" }`
  - `400 Bad Request` — invalid phone format.
  - `429 Too Many Requests` — rate limit exceeded.

#### 3.3.2. POST `/api/auth/phone/verify`

- **Description:** Verify SMS code, register new user or log in existing one.
- **Request Body:**
  ```json
  {
    "phone": "+7...",
    "code": "123456",
    "email": "user@example.com",    // required for new users
    "password": "P@ssw0rd!"        // required for new users
  }
  ```
- **Logic:**
  1. Lookup latest `sms_codes` entry by phone and `sent_at <= now()`.
  2. Check TTL (5 min) and `attempts < 5`.
  3. If incorrect code → increment `attempts`; if `attempts` reaches 5 → update `users.blocked_until = now() + 1h`.
  4. If new user: create `users` record (hash `password`), set `is_active = true`.
  5. Generate `access_token` (TTL=3600s) and `refresh_token` (TTL=30d or 60d if `remember_me`).
- **Responses:**
  - `200 OK` —
    ```json
    { "access_token": "...", "refresh_token": "...", "user": { /* user profile */ } }
    ```
  - `401 Unauthorized` — invalid or expired code.
  - `423 Locked` — phone number is temporarily blocked.

#### 3.3.3. POST `/api/auth/email/register`

- **Description:** Register with email and password for non-RU users.
- **Request Body:** `{ "email": "...", "password": "..." }`
- **Validation:**
  - Email format validation.
  - Password strength: min 8 characters, including letters and digits.
- **Logic:**
  - Create `users` record with `is_active = false`, generate `email_token` (UUID, TTL=24h), send confirmation email.
- **Response:** `200 OK`.

#### 3.3.4. GET `/api/auth/email/confirm?token=...`

- **Description:** Confirm email registration.
- **Query Param:** `token` (UUID from email).
- **Logic:**
  - Verify `email_token` exists and not expired.
  - Set `users.is_active = true`, clear `email_token`, invalidate all refresh tokens.
- **Response:** `302 Found` → redirect to frontend confirmation page.

#### 3.3.5. POST `/api/auth/email/login`

- **Description:** Log in via email and password.
- **Request Body:** `{ "email": "...", "password": "...", "remember_me": true|false }`
- **Logic:**
  - Verify password hash.
  - Generate `access_token` (TTL=1h) and `refresh_token` (TTL=30d or 60d if `remember_me`).
- **Responses:**
  - `200 OK` — tokens + user profile.
  - `401 Unauthorized` — invalid credentials.

#### 3.3.6. POST `/api/auth/email/forgot`

- **Description:** Request password reset.
- **Request Body:** `{ "email": "..." }`
- **Logic:**
  - Generate `reset_token` (UUID, TTL=15m), send password reset email.
- **Response:** `200 OK`.

#### 3.3.7. POST `/api/auth/email/reset`

- **Description:** Complete password reset.
- **Request Body:** `{ "token": "...", "new_password": "..." }`
- **Logic:**
  - Verify `reset_token`, update `password_hash`, invalidate all refresh tokens.
- **Response:** `200 OK`.

#### 3.3.8. POST `/api/auth/logout`

- **Description:** Invalidate a refresh token.
- **Request Body:** `{ "refresh_token": "..." }`
- **Logic:** Remove token record from `refresh_tokens`.
- **Response:** `204 No Content`.

---

## 4. Profile and Social Accounts Module

### 4.1. Use Cases (UC10–UC17)

Detailed use cases cover viewing/editing profile fields, uploading avatar, linking/unlinking social accounts via OAuth, viewing change history, and managing the experience-level lookup table.

### 4.2. Database Schema

```sql
CREATE TABLE profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id),
  first_name VARCHAR(100) NOT NULL,
  nickname VARCHAR(50),
  birth_date DATE,
  gender VARCHAR(10) CHECK (gender IN ('male','female','other')),
  country VARCHAR(100),
  city VARCHAR(100),
  company VARCHAR(150),
  position VARCHAR(150),
  experience_id INT REFERENCES experience_levels(id),
  avatar_url VARCHAR(255),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE experience_levels (
  id SERIAL PRIMARY KEY,
  label VARCHAR(50) NOT NULL,
  sequence INT NOT NULL
);

CREATE TABLE social_bindings (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  provider VARCHAR(20) CHECK (provider IN ('telegram','vkontakte','whatsapp')),
  provider_id VARCHAR(255),
  linked_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE profile_history (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  field VARCHAR(50) NOT NULL,
  old_value TEXT,
  new_value TEXT,
  changed_at TIMESTAMPTZ DEFAULT now(),
  changed_by UUID REFERENCES users(id)
);
```

### 4.3. REST API Endpoints

- **GET** `/api/profile` — Retrieve user profile and linked social accounts.
- **PUT** `/api/profile` — Update one or more profile fields; log changes to `profile_history`.
- **POST** `/api/profile/avatar` — Upload avatar image (JPEG/PNG ≤5MB); returns `{ "avatar_url": "..." }`.
- **GET/POST/PUT/DELETE** `/api/experience-levels` — Admin-only CRUD for experience lookup.
- **POST** `/api/profile/social/link` — Link social account: `{ provider, oauth_token }`.
- **DELETE** `/api/profile/social/:provider` — Unlink.
- **GET** `/api/profile/history?page=&per_page=` — Paginated change history.

---

## 5. Content Management Module

### 5.1. Use Cases (UC20–UC31)

Covers course lifecycle (create, update, soft-delete), section management, material CRUD (video & document), video transcoding status, and streaming.

### 5.2. Database Schema

```sql
CREATE TABLE courses (
  id UUID PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  language VARCHAR(2) CHECK (language IN ('ru','en')),
  created_by UUID REFERENCES users(id),
  status VARCHAR(10) CHECK (status IN ('draft','published','archived')),
  visibility VARCHAR(10) CHECK (visibility IN ('public','private')),
  tags TEXT[],
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE sections (
  id UUID PRIMARY KEY,
  course_id UUID REFERENCES courses(id),
  title VARCHAR(255) NOT NULL,
  sequence INT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE materials (
  id UUID PRIMARY KEY,
  section_id UUID REFERENCES sections(id),
  type VARCHAR(10) CHECK (type IN ('video','document')),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(10) CHECK (status IN ('draft','published')),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ
);

CREATE TABLE media_files (
  id UUID PRIMARY KEY,
  material_id UUID REFERENCES materials(id),
  original_url TEXT NOT NULL,
  size_bytes BIGINT,
  duration_sec INT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE transcode_jobs (
  id UUID PRIMARY KEY,
  media_file_id UUID REFERENCES media_files(id),
  bitrate_kbps INT,
  status VARCHAR(10) CHECK (status IN ('queued','processing','ready','failed')),
  output_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE documents (
  id UUID PRIMARY KEY,
  material_id UUID REFERENCES materials(id),
  file_url TEXT NOT NULL,
  mime_type VARCHAR(50),
  size_bytes BIGINT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 5.3. REST API Endpoints

- **GET** `/api/courses?status=&visibility=&tag=&page=&per_page=` — List courses.
- **POST** `/api/courses` — Create a course.
- **PUT** `/api/courses/:id` — Update course metadata and status.
- **DELETE** `/api/courses/:id` — Soft-delete.
- **GET** `/api/courses/:courseId/sections` — List sections.
- **POST** `/api/courses/:courseId/sections` — Create section.
- **PUT** `/api/sections/:id` — Update section title or sequence.
- **DELETE** `/api/sections/:id` — Soft-delete.
- **GET** `/api/sections/:sectionId/materials` — List materials (published for students).
- **POST** `/api/sections/:sectionId/materials` — Create material (draft).
- **PUT** `/api/materials/:id` — Update material metadata or status.
- **DELETE** `/api/materials/:id` — Soft-delete.
- **POST** `/api/materials/:id/upload` — Upload video or document file; trigger transcoding for videos.
- **GET** `/api/media/:mediaFileId/status` — Check transcode job statuses.
- **GET** `/api/media/:mediaFileId/stream?bitrate=` — Redirect to HLS/DASH stream URL.

---

## 6. Notification Module

### 6.1. Use Cases (UC40–UC45)

User notification preferences management, admin template CRUD, queued dispatch, and logs.

### 6.2. Database Schema

```sql
CREATE TABLE notification_types (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE,
  description VARCHAR(255)
);

CREATE TABLE user_notification_settings (
  user_id UUID REFERENCES users(id),
  notification_type_id INT REFERENCES notification_types(id),
  enabled BOOLEAN DEFAULT TRUE,
  via_email BOOLEAN DEFAULT TRUE,
  via_telegram BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY(user_id, notification_type_id)
);

CREATE TABLE notification_templates (
  id SERIAL PRIMARY KEY,
  notification_type_id INT REFERENCES notification_types(id),
  channel VARCHAR(10) CHECK (channel IN ('email','telegram')),
  subject VARCHAR(255),  -- for email
  body TEXT,              -- Mustache syntax
  updated_by UUID REFERENCES users(id),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE notification_queue (
  id UUID PRIMARY KEY,
  notification_type_id INT REFERENCES notification_types(id),
  user_id UUID REFERENCES users(id),
  channel VARCHAR(10) CHECK (channel IN ('email','telegram')),
  payload JSONB,
  status VARCHAR(10) CHECK (status IN ('pending','sent','failed')),
  attempts INT DEFAULT 0,
  last_error TEXT,
  scheduled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 6.3. REST API Endpoints

- **GET** `/api/notifications/settings` — Retrieve user preferences for each notification type.
- **PUT** `/api/notifications/settings` — Update multiple preferences in bulk.
- **GET** `/api/notifications/templates?notification_type_id=&channel=` — List templates.
- **POST** `/api/notifications/templates` — Create a template (admin only).
- **PUT** `/api/notifications/templates/:id` — Update subject/body (admin only).
- **DELETE** `/api/notifications/templates/:id` — Delete (admin only).
- **POST** `/internal/notifications/enqueue` — Enqueue a notification for a user based on event triggers.
- **GET** `/internal/notifications/queue?status=pending&limit=` — Fetch pending items.
- **POST** `/internal/notifications/queue/:id/send` — Process a queue item (dispatch via SMTP or Telegram bot).

---

## 7. Chat Module

### 7.1. Use Cases (UC50–UC58)

Personal and group chat flows, file attachments, moderation, message editing/deletion, real-time updates.

### 7.2. Database Schema

```sql
CREATE TABLE chats (
  id UUID PRIMARY KEY,
  type VARCHAR(10) CHECK (type IN ('personal','group')),
  course_id UUID REFERENCES courses(id),  -- null for personal chats
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chat_participants (
  chat_id UUID REFERENCES chats(id),
  user_id UUID REFERENCES users(id),
  joined_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY(chat_id, user_id)
);

CREATE TABLE messages (
  id UUID PRIMARY KEY,
  chat_id UUID REFERENCES chats(id),
  sender_id UUID REFERENCES users(id),
  content TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  edited_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ
);

CREATE TABLE attachments (
  id UUID PRIMARY KEY,
  message_id UUID REFERENCES messages(id),
  url TEXT NOT NULL,
  mime_type VARCHAR(100),
  size_bytes BIGINT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### 7.3. REST & WebSocket API

- **GET** `/api/chats` — List chats for current user.
- **GET** `/api/chats/:chatId/messages?limit=&offset=` — Fetch message history.
- **POST** `/api/chats/:chatId/messages` — Send message with optional file attachment (`multipart/form-data`).
- **PUT** `/api/chats/:chatId/messages/:messageId` — Edit own message (within 15 minutes).
- **DELETE** `/api/chats/:chatId/messages/:messageId` — Soft-delete own message.
- **DELETE** `/api/admin/chats/:chatId/messages/:messageId` — Moderator/admin deletion of any message.
- **WebSocket** `ws://.../ws/chats/:chatId` — Real-time events: `message.new`, `message.update`, `message.delete`.

---

## 8. Analytics and Reporting Module

### 8.1. Use Cases (UC60–UC65)

Dashboard metrics, on-demand report generation, download as PDF/XLSX, optional scheduled reports.

### 8.2. Database Schema

```sql
CREATE TABLE report_types (
  id SERIAL PRIMARY KEY,
  code VARCHAR(50) UNIQUE,
  description VARCHAR(255)
);

CREATE TABLE report_requests (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  report_type_id INT REFERENCES report_types(id),
  params JSONB,
  status VARCHAR(10) CHECK (status IN ('pending','processing','ready','failed')),
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE report_results (
  id UUID PRIMARY KEY,
  request_id UUID REFERENCES report_requests(id),
  format VARCHAR(10) CHECK (format IN ('pdf','xlsx')),
  file_url TEXT NOT NULL,
  size_bytes BIGINT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE report_schedules (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  report_type_id INT REFERENCES report_types(id),
  frequency VARCHAR(10) CHECK (frequency IN ('daily','weekly','monthly')),
  next_run TIMESTAMPTZ,
  active BOOLEAN DEFAULT true,
  params JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 8.3. REST API Endpoints

- **GET** `/api/analytics/dashboard` — Retrieve key metrics (course progress, activity, average scores, time spent).
- **GET** `/api/analytics/report-types` — List available report types.
- **POST** `/api/analytics/reports` — Request new report generation; returns `request_id` with status `pending`.
- **GET** `/api/analytics/reports?user_scope=own&status=&limit=&offset=` — List user's report requests.
- **GET** `/api/analytics/reports/:requestId` — Check status and detail of a report request.
- **GET** `/api/analytics/reports/:requestId/download?format=pdf|xlsx` — Download link (302 redirect) when `status=ready`; `409 Conflict` otherwise.
- **GET/POST/PUT/DELETE** `/api/analytics/schedules` — CRUD for scheduled reports (admin or user-specific if allowed).

---

## 9. Non-Functional Requirements

- **Security:** TLS v1.2+, AES-256 at rest, HSTS, CSP headers, regular penetration tests.
- **Performance:** p99 latency <200ms for API endpoints; support at least 20 concurrent active users with HPA.
- **Monitoring:** Prometheus for metrics, Grafana dashboards, Alertmanager for alerts.
- **Logging:** Centralized EFK (Elasticsearch, Fluentd, Kibana) stack, log all errors and warnings.
- **Backups:** Nightly PostgreSQL backups, retention for 7 days.
- **CI/CD:** GitLab CI/CD pipelines with unit, integration tests; promotion from `master` → `staging` → `prod`.
