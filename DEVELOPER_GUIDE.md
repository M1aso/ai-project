# 🚀 AI E-Learning Platform - Developer Guide

**Complete guide for developers working with the AI E-Learning Platform**

## 📋 Table of Contents

1. [Quick Setup](#quick-setup)
2. [Architecture Overview](#architecture-overview)
3. [Development Workflow](#development-workflow)
4. [API Testing](#api-testing)
5. [Debugging Commands](#debugging-commands)
6. [Security Guidelines](#security-guidelines)
7. [Database Management](#database-management)
8. [Deployment & CI/CD](#deployment--cicd)
9. [Troubleshooting](#troubleshooting)

## 🚀 Quick Setup

### Prerequisites
- **VPS**: Ubuntu 20.04+ with Docker and Kubernetes
- **GitHub**: Repository access with admin permissions
- **Local**: Git, curl, jq, kubectl (optional)

### 1-Minute Setup
```bash
# Clone and deploy
git clone https://github.com/M1aso/ai-project.git
cd ai-project
./scripts/setup-vps.sh dev

# Push to trigger deployment
git add . && git commit -m "Initial setup" && git push origin dev
```

### Access Points
- **API Gateway**: http://api.45.146.164.70.nip.io
- **API Documentation**: http://docs.45.146.164.70.nip.io
- **Monitoring**: http://grafana.45.146.164.70.nip.io (admin/admin123)

## 🏗️ Architecture Overview

### Microservices Stack
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Client    │───▶│ API Gateway │───▶│  Services   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                    ┌─────────────┐
                    │   Ingress   │
                    └─────────────┘
```

| Service | Language | Port | Database | Purpose |
|---------|----------|------|----------|---------|
| **Auth** | Python/FastAPI | 8001 | PostgreSQL | Authentication, JWT |
| **Profile** | Python/FastAPI | 8002 | PostgreSQL | User profiles, avatars |
| **Content** | Go/Chi | 8003 | PostgreSQL | Courses, materials |
| **Analytics** | Python/FastAPI | 8004 | PostgreSQL | Events, reporting |
| **Notifications** | Python/FastAPI | 8005 | PostgreSQL | Email, SMS, Telegram |
| **Chat** | Node.js/TypeScript | 8006 | PostgreSQL | Real-time messaging |
| **Content-Worker** | Python/Celery | - | - | Background processing |

### Infrastructure Components
- **API Gateway**: Envoy proxy with JWT validation
- **Database**: PostgreSQL with service-specific schemas
- **Cache**: Redis for sessions and caching
- **Queue**: RabbitMQ for async processing
- **Storage**: MinIO for files and media
- **Monitoring**: Prometheus + Grafana

## 🔄 Development Workflow

### Feature Development
```bash
# 1. Create feature branch
git checkout dev && git pull origin dev
git checkout -b feature/my-awesome-feature

# 2. Make changes
# ... code changes ...

# 3. Test locally (optional)
./scripts/run-all-tests.sh

# 4. Commit and push
git add .
git commit -m "feat: add awesome feature"
git push origin feature/my-awesome-feature

# 5. Create PR to dev → Auto-deploy after merge
```

### Hotfix Workflow
```bash
# 1. Create hotfix from main
git checkout main && git pull origin main
git checkout -b hotfix/critical-fix

# 2. Make minimal fix
# ... fix code ...

# 3. Test and deploy
git add . && git commit -m "fix: critical issue"
git push origin hotfix/critical-fix

# 4. PR to main → Auto-deploy to production
```

## 🧪 API Testing

### Complete User Workflow Test
```bash
# 1. Register user
curl -X POST "http://api.45.146.164.70.nip.io/api/auth/email/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# 2. Login and get token
TOKEN=$(curl -X POST "http://api.45.146.164.70.nip.io/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!"}' | \
  jq -r '.access_token')

# 3. Create profile
curl -X PUT "http://api.45.146.164.70.nip.io/api/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "bio": "Test user profile"
  }'

# 4. Upload avatar (get presign URL)
curl -X POST "http://api.45.146.164.70.nip.io/api/profile/avatar/presign" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "avatar.jpg",
    "content_type": "image/jpeg",
    "size": 102400
  }'

# 5. Create content (⚠️ Currently unprotected!)
curl -X POST "http://api.45.146.164.70.nip.io/api/content/courses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Course",
    "description": "Course description",
    "category": "technology"
  }'
```

### Authentication Testing
```bash
# Test endpoint protection
test_auth() {
  local endpoint=$1
  echo "Testing $endpoint"
  
  # Without token (should fail)
  curl -s "$endpoint" | jq .
  
  # With invalid token (should fail)
  curl -s -H "Authorization: Bearer invalid" "$endpoint" | jq .
  
  # With valid token (should work)
  curl -s -H "Authorization: Bearer $TOKEN" "$endpoint" | jq .
}

# Test all services
test_auth "http://api.45.146.164.70.nip.io/api/auth/me"
test_auth "http://api.45.146.164.70.nip.io/api/profile"
test_auth "http://api.45.146.164.70.nip.io/api/content/courses"
```

## 🔧 Debugging Commands

### Service Health Checks
```bash
# Check all pods
kubectl get pods -A

# Check specific service
kubectl get pods -n dev | grep auth

# Service logs
kubectl logs -f deployment/auth -n dev

# Service logs with timestamp
kubectl logs -f deployment/auth -n dev --timestamps

# Last 100 lines
kubectl logs deployment/auth -n dev --tail=100
```

### Database Debugging
```bash
# Connect to PostgreSQL
kubectl exec -it deployment/auth -n dev -- python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject'
from sqlalchemy import create_engine, text
engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM users'))
    print(f'Users count: {result.fetchone()[0]}')
"

# Check migration status
kubectl exec -it deployment/auth -n dev -- python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject'
from sqlalchemy import create_engine, text
engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    result = conn.execute(text('SELECT version_num FROM alembic_version_auth'))
    print(f'Migration version: {result.fetchone()[0]}')
"
```

### Performance Debugging
```bash
# Resource usage
kubectl top pods -n dev

# Service metrics
curl -s http://prometheus.45.146.164.70.nip.io/api/v1/query?query=up | jq .

# Check service endpoints
kubectl get endpoints -n dev

# Network debugging
kubectl exec -it deployment/auth -n dev -- nslookup postgresql.postgresql.svc.cluster.local
```

### Configuration Debugging
```bash
# Check environment variables
kubectl exec deployment/auth -n dev -- env | grep -E "(DATABASE|REDIS|JWT)"

# Check ConfigMaps
kubectl get configmaps -n dev

# Check Secrets
kubectl get secrets -n dev

# Describe deployment
kubectl describe deployment auth -n dev
```

## 🔒 Security Guidelines

### ⚠️ **CRITICAL SECURITY ISSUES** (As of 2025-08-26)

#### 1. Content Service - UNPROTECTED
```go
// ❌ CURRENT (No authentication)
r.Route("/api/content", func(api chi.Router) {
    api.Get("/courses", getCourses) // UNPROTECTED!
})

// ✅ REQUIRED FIX
r.Route("/api/content", func(api chi.Router) {
    api.Use(jwtAuthMiddleware) // ADD THIS
    api.Get("/courses", getCourses)
})
```

#### 2. Analytics Service - UNPROTECTED
```python
# ❌ CURRENT (No authentication)
@router.post("/ingest")
async def ingest_event(event: EventModel):  # UNPROTECTED!
    pass

# ✅ REQUIRED FIX  
@router.post("/ingest")
async def ingest_event(
    event: EventModel, 
    current_user: User = Depends(get_current_user)  # ADD THIS
):
```

### Security Testing Commands
```bash
# Test authentication on all services
for service in auth profile content analytics notifications; do
  echo "=== Testing $service ==="
  curl -s "http://api.45.146.164.70.nip.io/api/$service" | jq .
done

# Test with invalid tokens
for service in auth profile content analytics; do
  echo "=== Testing $service with invalid token ==="
  curl -s -H "Authorization: Bearer invalid" \
    "http://api.45.146.164.70.nip.io/api/$service" | jq .
done
```

## 🗃️ Database Management

### Migration Commands
```bash
# Run migrations for all services
./scripts/run-migrations.sh

# Check migration status
kubectl logs job/auth-migration -n dev
kubectl logs job/profile-migration -n dev
kubectl logs job/analytics-migration -n dev

# Manual migration (if needed)
kubectl exec deployment/auth -n dev -- python -m alembic upgrade head
```

### Database Schema
```sql
-- Service-specific tables
-- Auth: users, refresh_tokens, alembic_version_auth
-- Profile: profiles, experience_levels, social_bindings, profile_history, alembic_version_profile  
-- Analytics: events, metrics, alembic_version_analytics
-- Content: courses, sections, materials, media_assets (Go migrations)
```

### Backup Commands
```bash
# Create database backup
kubectl exec postgresql-0 -n postgresql -- pg_dump -U postgres aiproject > backup.sql

# Restore from backup
kubectl exec -i postgresql-0 -n postgresql -- psql -U postgres aiproject < backup.sql
```

## 🚀 Deployment & CI/CD

### CI/CD Pipeline
```mermaid
graph LR
    A[Push to dev] --> B[Unit Tests]
    B --> C[Contract Lint]
    C --> D[Build Images]
    D --> E[Deploy to Dev]
    E --> F[Integration Tests]
```

### Deployment Commands
```bash
# Manual deployment
helm upgrade --install auth deploy/helm/auth \
  --namespace dev \
  --set image.tag=latest

# Check deployment status
kubectl rollout status deployment/auth -n dev

# Rollback deployment
kubectl rollout undo deployment/auth -n dev
```

### Environment Management
```bash
# List environments
./scripts/manage-env.sh show

# Set environment variable
./scripts/manage-env.sh set dev auth LOG_LEVEL DEBUG

# Deploy specific service
./scripts/manage-env.sh deploy dev auth
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n dev

# Check logs
kubectl logs <pod-name> -n dev

# Check resource limits
kubectl top pod <pod-name> -n dev
```

#### 2. Database Connection Issues
```bash
# Test database connectivity
kubectl exec deployment/auth -n dev -- python -c "
import psycopg2
conn = psycopg2.connect('postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject')
print('Database connected successfully')
"

# Check database service
kubectl get svc -n postgresql
```

#### 3. Authentication Issues
```bash
# Check JWT secret
kubectl get secret jwt-secret -n dev -o yaml

# Test token validation
curl -X GET "http://api.45.146.164.70.nip.io/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. Image Pull Issues
```bash
# Check image pull secrets
kubectl get secrets -n dev | grep ghcr

# Check image exists
docker manifest inspect ghcr.io/m1aso/auth:latest
```

### Performance Issues
```bash
# Check resource usage
kubectl top pods -n dev

# Check service metrics
curl -s http://prometheus.45.146.164.70.nip.io/metrics

# Scale service
kubectl scale deployment auth --replicas=3 -n dev
```

### Network Issues
```bash
# Test service connectivity
kubectl exec deployment/auth -n dev -- curl http://profile:8000/healthz

# Check ingress
kubectl get ingress -n dev

# Test DNS resolution
kubectl exec deployment/auth -n dev -- nslookup profile.dev.svc.cluster.local
```

## 📊 Monitoring & Observability

### Key Metrics to Monitor
- **Response Time**: API endpoint latency
- **Error Rate**: HTTP 4xx/5xx responses
- **Throughput**: Requests per second
- **Resource Usage**: CPU/Memory/Disk
- **Database Performance**: Query time, connections

### Monitoring Commands
```bash
# Check Grafana dashboards
curl -s http://grafana.45.146.164.70.nip.io/api/health

# Query Prometheus metrics
curl -s 'http://prometheus.45.146.164.70.nip.io/api/v1/query?query=up' | jq .

# Service health checks
for service in auth profile content analytics notifications chat; do
  curl -s "http://api.45.146.164.70.nip.io/api/$service/healthz" | jq .
done
```

## 🎯 Best Practices

### Code Quality
- **Testing**: Write unit tests for all new features
- **Linting**: Use service-specific linters (pylint, golint, eslint)
- **Documentation**: Update OpenAPI specs for API changes
- **Security**: Never commit secrets or tokens

### Deployment
- **Feature Flags**: Use environment variables for feature toggles
- **Rolling Updates**: Always use rolling deployments
- **Health Checks**: Implement proper health and readiness probes
- **Monitoring**: Add metrics to all new endpoints

### Security
- **Authentication**: All endpoints must require valid JWT tokens
- **Authorization**: Implement proper role-based access control
- **Input Validation**: Validate and sanitize all inputs
- **Secrets Management**: Use Kubernetes secrets for sensitive data

---

## 📞 Support & Resources

### Documentation
- **API Docs**: http://docs.45.146.164.70.nip.io
- **Architecture**: [TECHNOLOGY_OVERVIEW.md](TECHNOLOGY_OVERVIEW.md)
- **Security**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)

### Useful Links
- **Repository**: https://github.com/M1aso/ai-project
- **Issues**: https://github.com/M1aso/ai-project/issues
- **CI/CD**: https://github.com/M1aso/ai-project/actions

### Emergency Contacts
- **Critical Issues**: Create GitHub issue with `critical` label
- **Security Issues**: Email security team immediately
- **Infrastructure**: Check Grafana alerts first

---

**Last Updated**: 2025-08-26  
**Version**: 1.0.0  
**Status**: ⚠️ CRITICAL SECURITY ISSUES IDENTIFIED - SEE SECURITY_AUDIT_REPORT.md