# Environment Variables Reference

## 📋 Overview

This document provides a comprehensive reference for all environment variables used across the AI Project microservices.

## 🌍 Environment Structure

| Environment | Branch | Deployment | Domain Pattern |
|-------------|--------|------------|----------------|
| **dev** | `dev` | Auto (on push) | `*.45.146.164.70.nip.io` |
| **staging** | `main` | Manual | `*.staging.45.146.164.70.nip.io` |
| **prod** | `release-*` tags | Auto (on tag) | `*.yourdomain.com` |

## 🔧 Service-Specific Environment Variables

### Auth Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis-master.redis.svc.cluster.local:6379` | Same as dev | Same as dev | Redis connection string |
| `JWT_SECRET` | `dev-jwt-secret-not-for-production` | `staging-jwt-secret-change-in-production` | From secret | JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | `HS256` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | `60` | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | `30` | `7` | Refresh token TTL |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

### Profile Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `MINIO_ENDPOINT` | `minio.minio.svc.cluster.local:9000` | Same as dev | Same as dev | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `admin` | `admin` | From secret | MinIO access key |
| `MINIO_SECRET_KEY` | `admin123456` | `admin123456` | From secret | MinIO secret key |
| `MINIO_SECURE` | `false` | `false` | `true` | Use HTTPS for MinIO |
| `MINIO_BUCKET` | `avatars` | `avatars` | `avatars` | Default bucket for avatars |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

### Content Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `MINIO_ENDPOINT` | `minio.minio.svc.cluster.local:9000` | Same as dev | Same as dev | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `admin` | `admin` | From secret | MinIO access key |
| `MINIO_SECRET_KEY` | `admin123456` | `admin123456` | From secret | MinIO secret key |
| `MINIO_SECURE` | `false` | `false` | `true` | Use HTTPS for MinIO |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

### Notifications Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis-master.redis.svc.cluster.local:6379` | Same as dev | Same as dev | Redis connection string |
| `RABBITMQ_URL` | `amqp://admin:admin123@rabbitmq.rabbitmq.svc.cluster.local:5672` | Same as dev | From secret | RabbitMQ connection string |
| `SMTP_HOST` | `smtp.gmail.com` | `smtp.gmail.com` | From secret | SMTP server host |
| `SMTP_PORT` | `587` | `587` | `587` | SMTP server port |
| `SMTP_USER` | Not set (dev) | From secret | From secret | SMTP username |
| `SMTP_PASSWORD` | Not set (dev) | From secret | From secret | SMTP password |
| `TELEGRAM_BOT_TOKEN` | Not set (dev) | From secret | From secret | Telegram bot token |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

### Chat Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis-master.redis.svc.cluster.local:6379` | Same as dev | Same as dev | Redis connection string |
| `MINIO_ENDPOINT` | `minio.minio.svc.cluster.local:9000` | Same as dev | Same as dev | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `admin` | `admin` | From secret | MinIO access key |
| `MINIO_SECRET_KEY` | `admin123456` | `admin123456` | From secret | MinIO secret key |
| `MINIO_SECURE` | `false` | `false` | `true` | Use HTTPS for MinIO |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

### Analytics Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis-master.redis.svc.cluster.local:6379` | Same as dev | Same as dev | Redis connection string |
| `RABBITMQ_URL` | `amqp://admin:admin123@rabbitmq.rabbitmq.svc.cluster.local:5672` | Same as dev | From secret | RabbitMQ connection string |
| `MINIO_ENDPOINT` | `minio.minio.svc.cluster.local:9000` | Same as dev | Same as dev | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `admin` | `admin` | From secret | MinIO access key |
| `MINIO_SECRET_KEY` | `admin123456` | `admin123456` | From secret | MinIO secret key |
| `MINIO_SECURE` | `false` | `false` | `true` | Use HTTPS for MinIO |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

### Content Worker Service

| Variable | Dev Value | Staging Value | Prod Value | Description |
|----------|-----------|---------------|------------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject` | Same as dev | From secret | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis-master.redis.svc.cluster.local:6379` | Same as dev | Same as dev | Redis connection string |
| `RABBITMQ_URL` | `amqp://admin:admin123@rabbitmq.rabbitmq.svc.cluster.local:5672` | Same as dev | From secret | RabbitMQ connection string |
| `MINIO_ENDPOINT` | `minio.minio.svc.cluster.local:9000` | Same as dev | Same as dev | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `admin` | `admin` | From secret | MinIO access key |
| `MINIO_SECRET_KEY` | `admin123456` | `admin123456` | From secret | MinIO secret key |
| `MINIO_SECURE` | `false` | `false` | `true` | Use HTTPS for MinIO |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | Logging level |

## 🔐 Secrets Management

### Production Secrets Setup

For production environment, create these Kubernetes secrets:

```bash
# Auth service secrets
kubectl create secret generic auth-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=jwt-secret="super-secure-jwt-secret-256-bit-key"

# Profile service secrets  
kubectl create secret generic profile-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=minio-access-key="prod-minio-access-key" \
  --from-literal=minio-secret-key="prod-minio-secret-key"

# Content service secrets
kubectl create secret generic content-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=minio-access-key="prod-minio-access-key" \
  --from-literal=minio-secret-key="prod-minio-secret-key"

# Notifications service secrets
kubectl create secret generic notifications-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=rabbitmq-url="amqp://prod_user:secure_password@prod-rabbitmq:5672" \
  --from-literal=smtp-user="your-production-email@company.com" \
  --from-literal=smtp-password="your-app-specific-password" \
  --from-literal=telegram-bot-token="your-production-telegram-bot-token"

# Chat service secrets
kubectl create secret generic chat-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=minio-access-key="prod-minio-access-key" \
  --from-literal=minio-secret-key="prod-minio-secret-key"

# Analytics service secrets
kubectl create secret generic analytics-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=rabbitmq-url="amqp://prod_user:secure_password@prod-rabbitmq:5672" \
  --from-literal=minio-access-key="prod-minio-access-key" \
  --from-literal=minio-secret-key="prod-minio-secret-key"

# Content worker secrets
kubectl create secret generic content-worker-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=rabbitmq-url="amqp://prod_user:secure_password@prod-rabbitmq:5672" \
  --from-literal=minio-access-key="prod-minio-access-key" \
  --from-literal=minio-secret-key="prod-minio-secret-key"
```

## 🛠️ Environment Management Commands

### Using the Management Script

```bash
# Make script executable
chmod +x scripts/manage-env.sh

# List all environment variables for auth service in dev
./scripts/manage-env.sh list dev auth

# Set a specific environment variable
./scripts/manage-env.sh set dev auth LOG_LEVEL DEBUG

# Get a specific environment variable
./scripts/manage-env.sh get dev auth DATABASE_URL

# Update service from values file
./scripts/manage-env.sh update dev auth

# Create/update secrets
./scripts/manage-env.sh secrets prod auth JWT_SECRET your-super-secret-key

# Redeploy service
./scripts/manage-env.sh deploy dev auth

# Show overview of all environments
./scripts/manage-env.sh show
```

### Manual Helm Commands

```bash
# Update single environment variable
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=DEBUG \
  --reuse-values

# Update multiple environment variables
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=DEBUG \
  --set env[1].name=JWT_SECRET \
  --set env[1].value=new-secret \
  --reuse-values

# Deploy with custom values
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  -f deploy/helm/auth/values.dev.yaml \
  --set image.tag=latest
```

### Direct Kubernetes Commands

```bash
# View current environment variables
kubectl get deployment auth -n dev -o yaml | grep -A 50 env:

# Edit deployment directly (not recommended)
kubectl edit deployment auth -n dev

# Create secret
kubectl create secret generic my-secret \
  --namespace=dev \
  --from-literal=key1=value1 \
  --from-literal=key2=value2

# Update secret
kubectl patch secret my-secret -n dev -p='{"data":{"key1":"'$(echo -n "new-value" | base64)'"}}'
```

## 📁 Configuration File Locations

### Helm Values Files
```
deploy/helm/
├── auth/
│   ├── values.yaml          # Base configuration
│   ├── values.dev.yaml      # Dev overrides
│   ├── values.staging.yaml  # Staging overrides
│   └── values.prod.yaml     # Production overrides
├── profile/
│   ├── values.yaml
│   ├── values.dev.yaml
│   └── ... (same pattern)
└── ... (other services)
```

### Environment-Specific Configurations
```bash
# Dev environment files
deploy/helm/*/values.dev.yaml

# Staging environment files  
deploy/helm/*/values.staging.yaml

# Production environment files
deploy/helm/*/values.prod.yaml
```

## 🔄 Environment Variable Update Workflow

### 1. Development Environment
```bash
# Edit the dev values file
vim deploy/helm/auth/values.dev.yaml

# Update the environment variables section
env:
  - name: NEW_VARIABLE
    value: "new-value"
  - name: LOG_LEVEL
    value: "DEBUG"

# Apply changes
./scripts/manage-env.sh update dev auth

# Or use Helm directly
helm upgrade auth deploy/helm/auth -n dev -f deploy/helm/auth/values.dev.yaml
```

### 2. Staging Environment
```bash
# Edit staging values file
vim deploy/helm/auth/values.staging.yaml

# Deploy to staging via GitHub Actions
# Go to: Actions > Deploy > Run workflow
# Select: staging environment, auth service
```

### 3. Production Environment
```bash
# Create/update production secrets first
kubectl create secret generic auth-secrets \
  --namespace=prod \
  --from-literal=jwt-secret="production-super-secure-key" \
  --from-literal=database-url="postgresql://prod_user:prod_pass@prod-db:5432/aiproject" \
  --dry-run=client -o yaml | kubectl apply -f -

# Edit production values file
vim deploy/helm/auth/values.prod.yaml

# Deploy via release tag
git tag release-1.0.1
git push origin release-1.0.1
```

## 🚨 Security Best Practices

### 1. Secret Rotation
```bash
# Rotate JWT secret
NEW_SECRET=$(openssl rand -base64 32)
kubectl patch secret auth-secrets -n prod -p="{\"data\":{\"jwt-secret\":\"$(echo -n $NEW_SECRET | base64)\"}}"

# Restart deployment to pick up new secret
kubectl rollout restart deployment auth -n prod
```

### 2. Environment Separation
- **Dev**: Uses hardcoded values for easy development
- **Staging**: Uses production-like secrets but with staging data
- **Prod**: All sensitive values stored in Kubernetes secrets

### 3. Secret Management
```bash
# View secret keys (not values)
kubectl get secret auth-secrets -n prod -o yaml

# Decode secret value (be careful!)
kubectl get secret auth-secrets -n prod -o jsonpath="{.data.jwt-secret}" | base64 -d

# Create secret from file
kubectl create secret generic tls-secret \
  --namespace=prod \
  --from-file=tls.crt=path/to/cert.crt \
  --from-file=tls.key=path/to/cert.key
```

## 📊 Monitoring Environment Variables

### Grafana Queries

Monitor environment variable changes:
```promql
# Track deployment restarts (indicates env var changes)
increase(kube_deployment_status_replicas_updated[5m])

# Monitor configuration errors
increase(prometheus_config_last_reload_successful == 0[5m])
```

### Alerting Rules

Create alerts for configuration issues:
```yaml
groups:
- name: config-alerts
  rules:
  - alert: ServiceConfigError
    expr: up{job="kubernetes-pods"} == 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Service {{ $labels.pod }} is down"
      description: "Service may have configuration issues"
```

## 🔍 Troubleshooting Environment Issues

### Common Problems

#### 1. Service Won't Start
```bash
# Check pod events
kubectl describe pod <pod-name> -n dev

# Check environment variables
kubectl get deployment auth -n dev -o yaml | grep -A 20 env:

# Check secrets
kubectl get secrets -n dev
kubectl describe secret auth-secrets -n dev
```

#### 2. Database Connection Issues
```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql "postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject"

# Check if DATABASE_URL is correct
./scripts/manage-env.sh get dev auth DATABASE_URL
```

#### 3. MinIO Connection Issues
```bash
# Test MinIO connectivity
kubectl run -it --rm debug --image=minio/mc --restart=Never -- \
  mc config host add myminio http://minio.minio.svc.cluster.local:9000 admin admin123456

# Check MinIO environment variables
./scripts/manage-env.sh list dev profile | grep MINIO
```

#### 4. Secret Not Found
```bash
# List all secrets in namespace
kubectl get secrets -n prod

# Check if secret exists and has correct keys
kubectl describe secret auth-secrets -n prod

# Recreate secret if needed
kubectl delete secret auth-secrets -n prod
./scripts/manage-env.sh secrets prod auth JWT_SECRET new-secret-value
```

## 📚 Quick Reference

### Environment Variable Patterns
```bash
# Database connections
DATABASE_URL="postgresql://user:pass@host:port/database"
REDIS_URL="redis://host:port"
RABBITMQ_URL="amqp://user:pass@host:port"

# MinIO configuration
MINIO_ENDPOINT="host:port"
MINIO_ACCESS_KEY="access-key"
MINIO_SECRET_KEY="secret-key"
MINIO_SECURE="true|false"

# Application settings
LOG_LEVEL="DEBUG|INFO|WARNING|ERROR"
JWT_SECRET="base64-encoded-secret"
PORT="8000"
```

### Useful Commands
```bash
# View all environment variables across services
for svc in auth profile content notifications chat analytics; do
  echo "=== $svc ==="
  ./scripts/manage-env.sh list dev $svc
  echo ""
done

# Check service health with environment info
kubectl get pods -n dev -o wide

# Monitor deployment status
watch kubectl get deployments -n dev
```