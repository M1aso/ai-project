# AI Project - Developer Guide

## 🚀 Quick Start

This guide covers everything a new developer needs to know to work with the AI Project - from local development to production debugging.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Local Development Setup](#local-development-setup)
3. [Building the Project](#building-the-project)
4. [Local Testing](#local-testing)
5. [Technology Stack](#technology-stack)
6. [Environment Variables](#environment-variables)
7. [Debugging & Monitoring](#debugging--monitoring)
8. [Development Workflows](#development-workflows)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

### Microservices Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │   Auth Service  │
│   (External)    │◄──►│   (Node.js)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
        ┌─────────▼───┐ ┌───────▼────┐ ┌──────▼─────┐
        │   Chat      │ │  Content   │ │  Profile   │
        │ (Node.js)   │ │   (Go)     │ │ (FastAPI)  │
        └─────────────┘ └────────────┘ └────────────┘
                 │              │              │
        ┌─────────▼───┐ ┌───────▼────┐ ┌──────▼─────┐
        │ Notifications│ │ Analytics  │ │Content     │
        │ (FastAPI)   │ │ (FastAPI)  │ │Worker      │
        └─────────────┘ └────────────┘ │(FastAPI)   │
                                       └────────────┘
```

### Infrastructure Components

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │   Redis     │  │  RabbitMQ   │
│ (Database)  │  │  (Cache)    │  │ (Messages)  │
└─────────────┘  └─────────────┘  └─────────────┘

┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   MinIO     │  │ Prometheus  │  │   Grafana   │
│ (Storage)   │  │(Monitoring) │  │(Dashboard)  │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 🔧 Local Development Setup

### Prerequisites

```bash
# Required tools
- Python 3.12+
- Node.js 18+
- Go 1.21+
- Docker & Docker Compose
- Git
```

### API Documentation Development

**Dynamic OpenAPI Generation**: Each service automatically generates its OpenAPI specification, eliminating the need for manual YAML maintenance.

**Local Service Documentation**:
```bash
# Start individual services and access their docs
cd services/auth && python -m uvicorn app.main:app --port 8000
# Visit: http://localhost:8000/api/auth/docs

cd services/profile && python -m uvicorn app.main:app --port 8001  
# Visit: http://localhost:8001/api/profile/docs

# Go service
cd services/content && go run cmd/server/main.go
# Visit: http://localhost:8002/api/content/docs

# Node.js service
cd services/chat && npm start
# Visit: http://localhost:8003/api/chats/docs
```

**Benefits for Developers**:
- ✅ **Code changes immediately reflect in docs**
- ✅ **No manual documentation updates required**
- ✅ **Interactive testing from documentation**
- ✅ **Professional API documentation with examples**

### 1. Clone Repository

```bash
git clone https://github.com/M1aso/ai-project.git
cd ai-project
```

### 2. Setup Development Environment

```bash
# Run the setup script
./scripts/setup-local-dev.sh

# Or manually:
# Install Python dependencies for each service
cd services/auth && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../analytics && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../notifications && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../profile && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cd ../content-worker && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Install Node.js dependencies
cd ../chat && npm install

# Install Go dependencies
cd ../content && go mod download
```

---

## 🏗️ Building the Project

### Option 1: Docker Build (Recommended)

```bash
# Build all services with docker-compose
docker-compose -f docker-compose.dev.yml build

# Build specific service
docker-compose -f docker-compose.dev.yml build auth

# Build and run all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f auth
```

### Option 2: Local Build (Without Docker)

#### Python Services (Auth, Analytics, Notifications, Profile, Content-Worker)

```bash
# Example for auth service
cd services/auth
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Node.js Services (API Gateway, Chat)

```bash
# Example for chat service
cd services/chat
npm install

# Build TypeScript
npm run build

# Start service
npm run dev
```

#### Go Services (Content)

```bash
# Content service
cd services/content

# Build
go build -o bin/server cmd/server/main.go

# Run
./bin/server
```

---

## 🧪 Local Testing

### Unit Tests

```bash
# Python services - run from service directory
cd services/auth
source venv/bin/activate
pytest tests/ -v

# Node.js services
cd services/chat
npm test

# Go services
cd services/content
go test ./...

# Run all tests
./scripts/run-all-tests.sh
```

### Integration Tests

```bash
# Start test environment
docker-compose -f docker-compose.dev.yml up -d

# Run integration tests
pytest tests/integration/ -v

# Performance tests
cd tests/perf
k6 run auth-smoke.js
```

### Manual API Testing

```bash
# Test auth registration
curl -X POST "http://localhost:8000/api/auth/email/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}'

# Test with different services
curl -X GET "http://localhost:8001/api/chat/health"
curl -X GET "http://localhost:8002/api/content/health"
```

---

## 🛠️ Technology Stack

### Core Technologies

| Service | Technology | Purpose | Port |
|---------|------------|---------|------|
| **Auth** | FastAPI + SQLAlchemy | Authentication & Authorization | 8000 |
| **API Gateway** | Node.js + Express | Request routing & rate limiting | 3000 |
| **Chat** | Node.js + Socket.IO | Real-time messaging | 8001 |
| **Content** | Go + Gin | Content management & file upload | 8002 |
| **Profile** | FastAPI + SQLAlchemy | User profile management | 8003 |
| **Analytics** | FastAPI + ClickHouse | Event tracking & analytics | 8004 |
| **Notifications** | FastAPI + Celery | Push/Email/SMS notifications | 8005 |
| **Content Worker** | FastAPI + Celery | Video transcoding & processing | 8006 |

### Infrastructure Components

#### PostgreSQL
- **Purpose**: Primary database for user data, profiles, auth
- **Port**: 5432
- **Usage**: Stores users, sessions, profiles, content metadata
- **Local Access**: `psql -h localhost -p 5432 -U postgres -d aiproject`

#### Redis
- **Purpose**: Caching, session storage, rate limiting
- **Port**: 6379
- **Usage**: Cache user sessions, rate limit counters, temporary data
- **Local Access**: `redis-cli -h localhost -p 6379`

#### RabbitMQ
- **Purpose**: Message queue for async processing
- **Port**: 5672 (AMQP), 15672 (Management UI)
- **Usage**: User registration events, email notifications, file processing
- **Management UI**: http://localhost:15672 (admin/admin123)

#### MinIO
- **Purpose**: Object storage for files, images, videos
- **Port**: 9000 (API), 9001 (Console)
- **Usage**: User avatars, course materials, uploaded content
- **Console**: http://localhost:9001 (minioadmin/minioadmin123)

#### MailHog (Development)
- **Purpose**: SMTP server for email testing
- **Port**: 1025 (SMTP), 8025 (Web UI)
- **Usage**: Captures all outgoing emails for testing
- **Web UI**: http://localhost:8025

---

## 🔧 Environment Variables

### Core Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/aiproject
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# RabbitMQ
RABBITMQ_URL=amqp://admin:admin123@localhost:5672

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_SECURE=false

# SMTP (Development - MailHog)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
FROM_EMAIL=noreply@aiproject-dev.com

# JWT & Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Service URLs
FRONTEND_URL=http://localhost:3000
API_GATEWAY_URL=http://localhost:3000
```

### Environment Files

```bash
# Copy example environment file
cp env.example .env

# Service-specific environment files
services/auth/env.example → services/auth/.env
```

### Variable Management

```bash
# Use the management script
./scripts/manage-env.sh

# Options:
# 1. Generate .env files for all services
# 2. Update specific service environment
# 3. Validate environment configuration
# 4. Show current environment status
```

---

## 🔍 Debugging & Monitoring

### Local Debugging

#### Application Logs

```bash
# Docker logs
docker-compose -f docker-compose.dev.yml logs -f [service_name]

# Examples:
docker-compose -f docker-compose.dev.yml logs -f auth
docker-compose -f docker-compose.dev.yml logs -f chat --tail=100

# Local service logs (if running without Docker)
# Python services use uvicorn logs
tail -f logs/auth.log

# Node.js services
npm run dev  # Shows logs in console

# Go services
./bin/server 2>&1 | tee logs/content.log
```

#### Database Debugging

```bash
# Connect to PostgreSQL
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -d aiproject

# Common queries
SELECT * FROM users ORDER BY created_at DESC LIMIT 5;
SELECT * FROM email_verifications WHERE expires_at > NOW();

# Check database connections
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity 
WHERE datname = 'aiproject';
```

#### Redis Debugging

```bash
# Connect to Redis
redis-cli -h localhost -p 6379

# Common commands
KEYS *                          # List all keys
GET "rate_limit:ip:127.0.0.1"  # Get rate limit data
FLUSHALL                        # Clear all data (development only)
INFO memory                     # Memory usage
MONITOR                         # Watch all commands in real-time
```

#### RabbitMQ Debugging

```bash
# Management UI
open http://localhost:15672

# Command line tools
rabbitmqctl list_queues
rabbitmqctl list_exchanges
rabbitmqctl list_bindings

# Check message flow
rabbitmqctl list_queues name messages consumers
```

### Production Debugging (Kubernetes)

#### Pod Management

```bash
# List pods
kubectl get pods -n dev

# Check pod status
kubectl describe pod auth-xxx-xxx -n dev

# Get pod logs
kubectl logs -f auth-xxx-xxx -n dev
kubectl logs auth-xxx-xxx -n dev --tail=100

# Execute commands in pod
kubectl exec -it auth-xxx-xxx -n dev -- bash
kubectl exec auth-xxx-xxx -n dev -- env | grep DATABASE
```

#### Service Debugging

```bash
# Check service endpoints
kubectl get svc -n dev
kubectl describe svc auth -n dev

# Test service connectivity
kubectl exec -it auth-xxx-xxx -n dev -- curl http://redis-master.redis.svc.cluster.local:6379

# Port forwarding for local access
kubectl port-forward svc/auth 8000:8000 -n dev
kubectl port-forward svc/postgresql 5432:5432 -n postgresql
```

#### Database Access (Production)

```bash
# SSH tunnel to production database
ssh -L 15432:localhost:5432 user@production-server

# Connect through tunnel
PGPASSWORD=production_password psql -h localhost -p 15432 -U postgres -d aiproject
```

### Monitoring with Grafana & Prometheus

#### Grafana Dashboard

```bash
# Local access
open http://localhost:3001

# Production access (if ingress configured)
open http://grafana.your-domain.com

# Default credentials: admin/admin (change on first login)
```

#### Key Dashboards

1. **AI Project Overview** (`/d/ai-project-overview`)
   - Service health status
   - Request rates and response times
   - Error rates by service
   - Database connection pools

2. **Infrastructure Metrics**
   - CPU, Memory, Disk usage
   - Network I/O
   - Pod restart counts

3. **Custom Metrics**
   - User registration rates
   - Authentication success/failure rates
   - File upload/processing stats

#### Prometheus Queries

```promql
# Service availability
up{job="auth-service"}

# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Database connections
postgres_connections{database="aiproject"}

# Memory usage
container_memory_usage_bytes{pod=~"auth-.*"}
```

#### Custom Alerts

```yaml
# Example alert rule
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value }} for {{ $labels.service }}"
```

---

## 🔄 Development Workflows

### Feature Development

```bash
# 1. Create feature branch
git checkout -b feature/user-profile-enhancement

# 2. Make changes and test locally
docker-compose -f docker-compose.dev.yml up -d
# ... develop and test ...

# 3. Run tests
./scripts/run-all-tests.sh

# 4. Commit and push
git add .
git commit -m "feat: add user profile enhancement"
git push origin feature/user-profile-enhancement

# 5. Create pull request
# 6. After review, merge to dev
# 7. Deploy to staging for integration testing
```

### Database Migrations

```bash
# Create new migration (example for auth service)
cd services/auth
source venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "add user preferences table"

# Review generated migration file
# Edit if necessary: services/auth/app/db/migrations/versions/xxx_add_user_preferences_table.py

# Apply migration locally
alembic upgrade head

# Test migration rollback
alembic downgrade -1
alembic upgrade head
```

### Adding New Service

```bash
# 1. Create service directory
mkdir services/new-service
cd services/new-service

# 2. Initialize based on technology:

# Python (FastAPI)
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy alembic
# Copy structure from existing service

# Node.js
npm init -y
npm install express typescript @types/node
# Copy structure from chat service

# Go
go mod init new-service
go get github.com/gin-gonic/gin
# Copy structure from content service

# 3. Add to docker-compose.dev.yml
# 4. Add Kubernetes manifests
# 5. Update documentation
```

---

## 🚨 Troubleshooting

### Common Issues

#### "Connection refused" errors

```bash
# Check if services are running
docker-compose -f docker-compose.dev.yml ps

# Check port conflicts
netstat -tulpn | grep :8000

# Restart specific service
docker-compose -f docker-compose.dev.yml restart auth
```

#### Database connection issues

```bash
# Check PostgreSQL status
docker-compose -f docker-compose.dev.yml logs postgresql

# Test connection
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -c "SELECT 1"

# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgresql
# Wait for startup, then run migrations
```

#### Redis connection issues

```bash
# Check Redis status
docker-compose -f docker-compose.dev.yml logs redis

# Test connection
redis-cli -h localhost -p 6379 ping

# Clear Redis data
redis-cli -h localhost -p 6379 FLUSHALL
```

#### Email not sending (MailHog)

```bash
# Check MailHog status
docker-compose -f docker-compose.dev.yml logs mailhog

# Check if emails are captured
curl http://localhost:8025/api/v2/messages

# Verify SMTP configuration
grep SMTP services/auth/.env
```

#### File upload issues (MinIO)

```bash
# Check MinIO status
docker-compose -f docker-compose.dev.yml logs minio

# Test MinIO connectivity
curl http://localhost:9000/minio/health/live

# Access MinIO console
open http://localhost:9001
```

### Performance Issues

#### Slow API responses

```bash
# Check database query performance
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -d aiproject
\x on
SELECT query, mean_time, calls, total_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### Memory leaks

```bash
# Monitor memory usage
docker stats

# Check specific service
docker-compose -f docker-compose.dev.yml exec auth top
```

#### High CPU usage

```bash
# Profile Python services
pip install py-spy
py-spy top --pid $(pgrep -f "uvicorn.*auth")

# Profile Node.js services
npm install -g clinic
clinic doctor -- node dist/index.js
```

---

## 📚 Additional Resources

### Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [API Quick Reference](./API_QUICK_REFERENCE.md)
- [Environment Variables Guide](./ENVIRONMENT_VARIABLES_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Local Development Guide](./LOCAL_DEVELOPMENT_GUIDE.md)

### Useful Commands

```bash
# Quick development setup
./scripts/setup-local-dev.sh

# Run all tests
./scripts/run-all-tests.sh

# Database migrations
./scripts/run-migrations.sh

# Environment management
./scripts/manage-env.sh

# Service verification
./scripts/verify-services.sh

# Deployment diagnosis
./scripts/diagnose-routing.sh
```

### IDE Configuration

#### VS Code Extensions
- Python
- Go
- TypeScript and JavaScript
- Docker
- Kubernetes
- REST Client
- GitLens

#### Recommended Settings
```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "go.toolsManagement.autoUpdate": true,
  "typescript.preferences.importModuleSpecifier": "relative",
  "docker.defaultRegistryPath": "your-registry.com"
}
```

---

## 🤝 Contributing

1. Follow the feature development workflow
2. Write tests for new functionality
3. Update documentation
4. Follow code style guidelines:
   - Python: Black + isort
   - TypeScript: Prettier + ESLint
   - Go: gofmt + golint

## 📞 Support

- **Issues**: Create GitHub issues for bugs and feature requests
- **Documentation**: Update this guide when adding new features
- **Questions**: Use GitHub discussions for development questions

---

*This guide is a living document. Please keep it updated as the project evolves!*
