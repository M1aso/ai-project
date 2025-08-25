# 🏠 Local Development Guide

A comprehensive guide to build and run the AI E-Learning Platform locally for development.

> 📚 **New Developer?** Check out the [**Developer Guide**](./DEVELOPER_GUIDE.md) for a complete overview including architecture, debugging, and production deployment. Also see the [**Debug Cheat Sheet**](./DEBUG_CHEATSHEET.md) for quick troubleshooting commands.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Infrastructure Setup](#infrastructure-setup)
4. [Service-by-Service Setup](#service-by-service-setup)
5. [Development Workflow](#development-workflow)
6. [Troubleshooting](#troubleshooting)
7. [Useful Commands](#useful-commands)

---

## 📦 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: At least 10GB free space
- **Docker**: Version 20.0+
- **Docker Compose**: Version 2.0+

### Required Tools

```bash
# 1. Install Docker and Docker Compose
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 2. Install development tools
sudo apt-get install -y git curl wget jq make

# 3. Install language-specific tools
# Python 3.9+
sudo apt-get install -y python3 python3-pip python3-venv

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Go 1.21+
wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/M1aso/ai-project.git
cd ai-project
```

### 2. Start Infrastructure Services

```bash
# Start all infrastructure services
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready (takes ~2-3 minutes)
./scripts/wait-for-services.sh
```

### 3. Setup and Start All Services

```bash
# Make setup script executable
chmod +x scripts/setup-local-dev.sh

# Run the setup script (installs dependencies and starts all services)
./scripts/setup-local-dev.sh

# Or start services individually (see Service-by-Service Setup section)
```

### 4. Verify Everything is Running

```bash
# Check infrastructure services
docker-compose -f docker-compose.dev.yml ps

# Check application services
./scripts/check-services.sh

# Access services:
# - API Gateway: http://localhost:8080
# - Auth Service: http://localhost:8000
# - Profile Service: http://localhost:8002
# - Content Service: http://localhost:8003
# - Notifications Service: http://localhost:8004
# - Chat Service: http://localhost:8005
# - Analytics Service: http://localhost:8006
```

---

## 🏗️ Infrastructure Setup

### Docker Compose for Infrastructure

Create the infrastructure services with Docker Compose:

```bash
# Start all infrastructure services
docker-compose -f docker-compose.dev.yml up -d

# Services included:
# - PostgreSQL (port 5432)
# - Redis (port 6379)
# - RabbitMQ (port 5672, management UI: 15672)
# - MinIO (API: 9000, Console: 9001)
# - Prometheus (port 9090)
# - Grafana (port 3000)
```

### Infrastructure Service Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **PostgreSQL** | `localhost:5432` | `postgres/postgres123` |
| **Redis** | `localhost:6379` | No auth |
| **RabbitMQ Management** | http://localhost:15672 | `admin/admin123` |
| **MinIO Console** | http://localhost:9001 | `admin/admin123456` |
| **MinIO API** | http://localhost:9000 | `admin/admin123456` |
| **Grafana** | http://localhost:3000 | `admin/admin123` |
| **Prometheus** | http://localhost:9090 | No auth |

---

## 🔧 Service-by-Service Setup

### Auth Service (Python/FastAPI)

```bash
cd services/auth

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="local-dev-jwt-secret-not-for-production"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
export REFRESH_TOKEN_EXPIRE_DAYS="30"
export LOG_LEVEL="DEBUG"

# Run database migrations
alembic upgrade head

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the provided script
./start-dev.sh
```

### Profile Service (Python/FastAPI)

```bash
cd services/profile

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export MINIO_BUCKET="avatars"
export LOG_LEVEL="DEBUG"

# Run database migrations
alembic upgrade head

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Content Service (Go)

```bash
cd services/content

# Install dependencies
go mod download

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"
export PORT="8003"

# Run database migrations
go run internal/db/migrations/migrate.go

# Build and start the service
go build -o bin/content cmd/server/main.go
./bin/content

# Or for development with hot reload
go run cmd/server/main.go
```

### Notifications Service (Python/FastAPI)

```bash
cd services/notifications

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export RABBITMQ_URL="amqp://admin:admin123@localhost:5672"
export LOG_LEVEL="DEBUG"

# Optional: Set email/telegram credentials for testing
# export SMTP_HOST="smtp.gmail.com"
# export SMTP_PORT="587"
# export SMTP_USER="your-email@gmail.com"
# export SMTP_PASSWORD="your-app-password"
# export TELEGRAM_BOT_TOKEN="your-bot-token"

# Start the main service
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# In another terminal, start the worker
cd services/notifications
source venv/bin/activate
python app/worker.py
```

### Chat Service (Node.js/TypeScript)

```bash
cd services/chat

# Install dependencies
npm install

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"
export PORT="8005"

# Run database migrations
npm run migrate

# Build TypeScript
npm run build

# Start the service
npm start

# Or for development with hot reload
npm run dev
```

### Analytics Service (Python/FastAPI)

```bash
cd services/analytics

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export RABBITMQ_URL="amqp://admin:admin123@localhost:5672"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"

# Run database migrations
alembic upgrade head

# Start the main service
uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload

# In another terminal, start the worker
cd services/analytics
source venv/bin/activate
python app/worker.py
```

### Content Worker Service (Python/Celery)

```bash
cd services/content-worker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export RABBITMQ_URL="amqp://admin:admin123@localhost:5672"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"

# Start the worker
python app/worker.py
```

---

## 🔄 Development Workflow

### Daily Development Routine

1. **Start Infrastructure**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Start Services** (in separate terminals):
   ```bash
   # Terminal 1: Auth Service
   cd services/auth && source venv/bin/activate && ./start-dev.sh
   
   # Terminal 2: Profile Service  
   cd services/profile && source venv/bin/activate && ./start-dev.sh
   
   # Terminal 3: Content Service
   cd services/content && go run cmd/server/main.go
   
   # Terminal 4: Chat Service
   cd services/chat && npm run dev
   
   # Terminal 5: Notifications Service + Worker
   cd services/notifications && source venv/bin/activate && ./start-dev.sh
   
   # Terminal 6: Analytics Service + Worker
   cd services/analytics && source venv/bin/activate && ./start-dev.sh
   
   # Terminal 7: Content Worker
   cd services/content-worker && source venv/bin/activate && python app/worker.py
   ```

3. **Development Tools**:
   ```bash
   # Run tests for a specific service
   cd services/auth && python -m pytest
   cd services/chat && npm test
   cd services/content && go test ./...
   
   # Check code formatting
   cd services/auth && black . && isort .
   cd services/chat && npm run lint
   cd services/content && go fmt ./...
   
   # View logs
   docker-compose -f docker-compose.dev.yml logs -f postgres
   docker-compose -f docker-compose.dev.yml logs -f redis
   ```

### Making Changes

1. **Database Schema Changes**:
   ```bash
   # For Python services (Auth, Profile, Notifications, Analytics)
   cd services/auth
   alembic revision --autogenerate -m "Add new table"
   alembic upgrade head
   
   # For Go service (Content)
   cd services/content
   # Edit migration files in internal/db/migrations/
   go run internal/db/migrations/migrate.go
   
   # For Node.js service (Chat)
   cd services/chat
   # Edit migration files in src/db/migrations/
   npm run migrate
   ```

2. **API Changes**:
   - OpenAPI specs are now automatically generated by services - no manual updates needed
   - Update service code
   - Update tests
   - Test with other services

3. **Environment Variables**:
   - Update local `.env` files or export statements
   - Update Helm values in `deploy/helm/*/values.dev.yaml`

### Testing

```bash
# Run all tests
./scripts/run-all-tests.sh

# Run tests for specific service
cd services/auth && python -m pytest tests/ -v
cd services/profile && python -m pytest tests/ -v  
cd services/content && go test ./... -v
cd services/chat && npm test
cd services/notifications && python -m pytest tests/ -v
cd services/analytics && python -m pytest tests/ -v

# Integration tests
cd tests && python -m pytest test_integration.py -v

# Load testing
cd tests/perf && node auth-smoke.js
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check if ports are available
netstat -tlnp | grep -E ':(8000|8002|8003|8004|8005|8006|5432|6379|5672|9000|9001)'

# Check infrastructure services
docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml logs postgres
docker-compose -f docker-compose.dev.yml logs redis

# Kill processes using ports
sudo lsof -ti:8000 | xargs kill -9
```

#### 2. Database Connection Issues

```bash
# Test PostgreSQL connection
psql postgresql://postgres:postgres123@localhost:5432/aiproject

# Check if database exists
psql postgresql://postgres:postgres123@localhost:5432/postgres -c "\l"

# Create database if missing
psql postgresql://postgres:postgres123@localhost:5432/postgres -c "CREATE DATABASE aiproject;"

# Reset database
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres
sleep 10
# Re-run migrations for all services
```

#### 3. MinIO Connection Issues

```bash
# Test MinIO connection
curl http://localhost:9000/minio/health/live

# Access MinIO Console
open http://localhost:9001
# Login: admin/admin123456

# Create buckets if missing
mc alias set local http://localhost:9000 admin admin123456
mc mb local/avatars
mc mb local/content
mc mb local/reports
```

#### 4. Redis Connection Issues

```bash
# Test Redis connection
redis-cli -p 6379 ping

# Check Redis info
redis-cli -p 6379 info

# Clear Redis cache if needed
redis-cli -p 6379 flushall
```

#### 5. RabbitMQ Issues

```bash
# Check RabbitMQ status
curl -u admin:admin123 http://localhost:15672/api/overview

# Access RabbitMQ Management
open http://localhost:15672
# Login: admin/admin123

# Restart RabbitMQ
docker-compose -f docker-compose.dev.yml restart rabbitmq
```

### Service-Specific Issues

#### Python Services (Auth, Profile, Notifications, Analytics)

```bash
# Virtual environment issues
cd services/auth
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Migration issues
alembic downgrade base
alembic upgrade head

# Dependency conflicts
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Go Service (Content)

```bash
# Module issues
cd services/content
go clean -modcache
go mod download
go mod tidy

# Build issues
go clean
go build -o bin/content cmd/server/main.go

# Database migration issues
go run internal/db/migrations/migrate.go reset
go run internal/db/migrations/migrate.go up
```

#### Node.js Service (Chat)

```bash
# Node modules issues
cd services/chat
rm -rf node_modules package-lock.json
npm install

# TypeScript compilation issues
npm run build

# Migration issues
npm run migrate:reset
npm run migrate
```

---

## 📝 Useful Commands

### Infrastructure Management

```bash
# Start all infrastructure services
docker-compose -f docker-compose.dev.yml up -d

# Stop all infrastructure services
docker-compose -f docker-compose.dev.yml down

# View logs
docker-compose -f docker-compose.dev.yml logs -f [service-name]

# Reset all data (CAUTION: Deletes all data)
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Service Management

```bash
# Check all service status
./scripts/check-services.sh

# Start all services
./scripts/start-all-services.sh

# Stop all services
./scripts/stop-all-services.sh

# Restart specific service
./scripts/restart-service.sh auth
```

### Database Operations

```bash
# Connect to PostgreSQL
psql postgresql://postgres:postgres123@localhost:5432/aiproject

# Backup database
pg_dump postgresql://postgres:postgres123@localhost:5432/aiproject > backup.sql

# Restore database
psql postgresql://postgres:postgres123@localhost:5432/aiproject < backup.sql

# Run migrations for all services
./scripts/run-migrations.sh
```

### Development Helpers

```bash
# Format all code
./scripts/format-code.sh

# Run all tests
./scripts/run-all-tests.sh

# Check service health
curl http://localhost:8000/healthz  # Auth
curl http://localhost:8002/healthz  # Profile
curl http://localhost:8003/healthz  # Content
curl http://localhost:8004/healthz  # Notifications
curl http://localhost:8005/healthz  # Chat
curl http://localhost:8006/healthz  # Analytics

# View API documentation
open http://localhost:8000/docs  # Auth API
open http://localhost:8002/docs  # Profile API
# etc.
```

### Monitoring and Debugging

```bash
# View Grafana dashboards
open http://localhost:3000

# View Prometheus metrics
open http://localhost:9090

# Monitor resource usage
docker stats

# View service logs
tail -f services/auth/logs/app.log
tail -f services/content/logs/app.log
# etc.
```

---

## 🚀 Next Steps

After setting up the local development environment:

1. **Explore the APIs**: Visit http://localhost:8000/docs for Auth API documentation
2. **Run the tests**: Execute `./scripts/run-all-tests.sh`
3. **Make your first change**: Try updating a service and see hot reload in action
4. **Check monitoring**: Visit http://localhost:3000 for Grafana dashboards
5. **Read the documentation**: Check `REQUIREMENTS.md` for detailed project requirements

## 📚 Additional Resources

- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Environment Variables Reference](ENV_REFERENCE.md)
- [Requirements Specification](REQUIREMENTS.md)
- [Quick Start Guide](QUICK_START.md)

---

**Happy coding! 🎉**
