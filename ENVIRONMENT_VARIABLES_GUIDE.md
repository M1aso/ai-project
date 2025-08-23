# 🌍 Complete Environment Variables Guide for AI Project

## 📋 Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Environment Variable Management Methods](#environment-variable-management-methods)
4. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
5. [Development Workflow](#development-workflow)
6. [Production Deployment](#production-deployment)
7. [Security Best Practices](#security-best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Quick Reference](#quick-reference)

## 📖 Overview

This AI project uses **Helm charts** for environment variable management across multiple microservices deployed on Kubernetes. The project supports three environments:

- **dev**: Development environment with debug settings
- **staging**: Pre-production environment for testing
- **prod**: Production environment with security-focused configuration

## 🏗️ Project Structure

Your project follows this environment variable architecture:

```
ai-project/
├── deploy/helm/                    # Helm charts for each service
│   ├── auth/
│   │   ├── values.yaml            # Base configuration
│   │   ├── values.dev.yaml        # Development overrides
│   │   ├── values.staging.yaml    # Staging overrides
│   │   ├── values.prod.yaml       # Production overrides
│   │   └── templates/
│   │       └── deployment.yaml    # Kubernetes deployment template
│   ├── profile/                   # Same structure for each service
│   ├── content/
│   ├── notifications/
│   ├── chat/
│   ├── analytics/
│   └── content-worker/
├── services/                      # Service source code
│   ├── auth/
│   │   └── env.example           # Development reference only
│   └── ...
├── scripts/
│   └── manage-env.sh             # Environment management script
└── ENV_REFERENCE.md              # Complete variable reference
```

## 🔧 Environment Variable Management Methods

### Method 1: Using the Management Script (Recommended)

The `scripts/manage-env.sh` script provides a convenient interface for all environment operations:

```bash
# Make script executable
chmod +x scripts/manage-env.sh

# List all environment variables for a service
./scripts/manage-env.sh list dev auth

# Set a single environment variable
./scripts/manage-env.sh set dev auth LOG_LEVEL DEBUG

# Get a specific environment variable
./scripts/manage-env.sh get dev auth DATABASE_URL

# Update service from values file
./scripts/manage-env.sh update dev auth

# Create/update secrets
./scripts/manage-env.sh secrets dev auth JWT_SECRET my-secret-key

# Redeploy service
./scripts/manage-env.sh deploy dev auth

# Show overview of all environments
./scripts/manage-env.sh show
```

### Method 2: Direct Helm Commands

For advanced users or CI/CD pipelines:

```bash
# Update single environment variable
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=DEBUG \
  --reuse-values

# Deploy with custom values file
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  -f deploy/helm/auth/values.dev.yaml \
  --set image.tag=latest
```

### Method 3: Direct Kubernetes Commands

For debugging or emergency changes:

```bash
# View current environment variables
kubectl get deployment auth -n dev -o yaml | grep -A 50 env:

# Edit deployment directly (not recommended for production)
kubectl edit deployment auth -n dev
```

## 🚀 Step-by-Step Setup Guide

### Step 1: Set Up Your Development Environment

1. **Clone and navigate to the project:**
   ```bash
   cd /home/pavel/Документы/ai-project
   ```

2. **Make the management script executable:**
   ```bash
   chmod +x scripts/manage-env.sh
   ```

3. **Verify your Kubernetes cluster is running:**
   ```bash
   kubectl cluster-info
   ```

### Step 2: Configure Environment Variables for Development

1. **Edit the development values file for a service:**
   ```bash
   # Example: Configure auth service for development
   vim deploy/helm/auth/values.dev.yaml
   ```

2. **Add or modify environment variables:**
   ```yaml
   env:
     # Database Configuration
     - name: DATABASE_URL
       value: "postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject"
     
     # JWT Security Configuration
     - name: JWT_SECRET_KEY
       value: "dev-jwt-secret-not-for-production"
     
     # Application Settings
     - name: LOG_LEVEL
       value: "DEBUG"
     - name: DEBUG
       value: "true"
   ```

3. **Apply the changes:**
   ```bash
   ./scripts/manage-env.sh update dev auth
   ```

### Step 3: Set Up Environment Variables for All Services

For each service (auth, profile, content, notifications, chat, analytics, content-worker):

1. **Check existing configuration:**
   ```bash
   ./scripts/manage-env.sh list dev [service-name]
   ```

2. **Edit values file if needed:**
   ```bash
   vim deploy/helm/[service-name]/values.dev.yaml
   ```

3. **Apply changes:**
   ```bash
   ./scripts/manage-env.sh update dev [service-name]
   ```

### Step 4: Create Kubernetes Namespaces

```bash
# Create namespaces for all environments
kubectl create namespace dev
kubectl create namespace staging  
kubectl create namespace prod
```

### Step 5: Deploy Services

```bash
# Deploy all services to development
for service in auth profile content notifications chat analytics content-worker; do
  ./scripts/manage-env.sh deploy dev $service
done
```

## 🔄 Development Workflow

### Adding a New Environment Variable

1. **Add to the appropriate values file:**
   ```bash
   vim deploy/helm/auth/values.dev.yaml
   ```

2. **Add the variable to the env section:**
   ```yaml
   env:
     - name: NEW_VARIABLE
       value: "new-value"
   ```

3. **Update the service:**
   ```bash
   ./scripts/manage-env.sh update dev auth
   ```

4. **Verify the change:**
   ```bash
   ./scripts/manage-env.sh get dev auth NEW_VARIABLE
   ```

### Updating Existing Environment Variables

1. **Using the management script:**
   ```bash
   ./scripts/manage-env.sh set dev auth LOG_LEVEL INFO
   ```

2. **Or edit the values file and update:**
   ```bash
   vim deploy/helm/auth/values.dev.yaml
   ./scripts/manage-env.sh update dev auth
   ```

### Environment-Specific Configuration

Each environment has its own configuration file:

- **Development (`values.dev.yaml`)**: Debug enabled, verbose logging, dev database
- **Staging (`values.staging.yaml`)**: Production-like settings with staging data
- **Production (`values.prod.yaml`)**: Secure settings, secrets from Kubernetes secrets

Example differences:

```yaml
# values.dev.yaml
env:
  - name: LOG_LEVEL
    value: "DEBUG"
  - name: JWT_SECRET_KEY
    value: "dev-jwt-secret"

# values.prod.yaml
env:
  - name: LOG_LEVEL
    value: "WARNING"
  - name: JWT_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: auth-secrets
        key: jwt-secret
```

## 🔐 Production Deployment

### Step 1: Create Production Secrets

```bash
# Create secrets for auth service
kubectl create secret generic auth-secrets \
  --namespace=prod \
  --from-literal=jwt-secret="$(openssl rand -base64 32)" \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject"

# Create secrets for profile service
kubectl create secret generic profile-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=minio-access-key="prod-minio-access-key" \
  --from-literal=minio-secret-key="prod-minio-secret-key"

# Create secrets for notifications service
kubectl create secret generic notifications-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://prod_user:secure_password@prod-db-host:5432/aiproject" \
  --from-literal=smtp-user="your-production-email@company.com" \
  --from-literal=smtp-password="your-app-specific-password" \
  --from-literal=telegram-bot-token="your-production-telegram-bot-token"
```

### Step 2: Configure Production Values

Edit `deploy/helm/auth/values.prod.yaml`:

```yaml
env:
  # Use secrets for sensitive values
  - name: JWT_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: auth-secrets
        key: jwt-secret
  
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: auth-secrets
        key: database-url
  
  # Non-sensitive production values
  - name: LOG_LEVEL
    value: "WARNING"
  - name: DEBUG
    value: "false"
  - name: ACCESS_TOKEN_TTL
    value: "900"  # 15 minutes in production
```

### Step 3: Deploy to Production

```bash
# Deploy services to production
./scripts/manage-env.sh deploy prod auth
./scripts/manage-env.sh deploy prod profile
# ... repeat for other services
```

## 🔒 Security Best Practices

### 1. Secret Management

- **Never commit secrets to Git**
- **Use Kubernetes secrets for production**
- **Rotate secrets regularly**
- **Use different secrets for each environment**

```bash
# Generate secure random secrets
openssl rand -base64 32  # For JWT secrets
openssl rand -hex 16     # For API keys
```

### 2. Environment Separation

| Environment | Security Level | Secret Storage | Database |
|-------------|---------------|----------------|----------|
| **dev** | Low | Hardcoded values | Shared dev DB |
| **staging** | Medium | K8s secrets | Staging DB |
| **prod** | High | K8s secrets + encryption | Production DB |

### 3. Secret Rotation

```bash
# Rotate JWT secret in production
NEW_JWT_SECRET=$(openssl rand -base64 32)
kubectl patch secret auth-secrets -n prod -p="{\"data\":{\"jwt-secret\":\"$(echo -n $NEW_JWT_SECRET | base64)\"}}"

# Restart deployment to pick up new secret
kubectl rollout restart deployment auth -n prod
```

### 4. Access Control

```bash
# Create service account with limited permissions
kubectl create serviceaccount env-manager -n prod

# Create role for environment management
kubectl create role env-manager \
  --verb=get,list,patch,update \
  --resource=deployments,secrets \
  -n prod

# Bind role to service account
kubectl create rolebinding env-manager-binding \
  --role=env-manager \
  --serviceaccount=prod:env-manager \
  -n prod
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Service Won't Start After Environment Change

**Symptoms:**
- Pod in CrashLoopBackOff state
- "ImagePullBackOff" errors

**Diagnosis:**
```bash
# Check pod status
kubectl get pods -n dev

# Check pod events
kubectl describe pod <pod-name> -n dev

# Check logs
kubectl logs <pod-name> -n dev
```

**Solutions:**
```bash
# Verify environment variables are set correctly
./scripts/manage-env.sh list dev auth

# Check if secrets exist (for prod environment)
kubectl get secrets -n prod

# Restart deployment
kubectl rollout restart deployment auth -n dev
```

#### 2. Environment Variable Not Taking Effect

**Symptoms:**
- Old value still being used
- Configuration not applied

**Diagnosis:**
```bash
# Check if deployment was updated
kubectl get deployment auth -n dev -o yaml | grep -A 20 env:

# Check deployment revision
kubectl rollout history deployment auth -n dev
```

**Solutions:**
```bash
# Force deployment update
kubectl rollout restart deployment auth -n dev

# Or update with --force
helm upgrade auth deploy/helm/auth -n dev -f deploy/helm/auth/values.dev.yaml --force
```

#### 3. Database Connection Issues

**Symptoms:**
- "Connection refused" errors
- Database timeout errors

**Diagnosis:**
```bash
# Test database connectivity from within cluster
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql "postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject"

# Check DATABASE_URL environment variable
./scripts/manage-env.sh get dev auth DATABASE_URL
```

#### 4. Secret Not Found

**Symptoms:**
- "Secret not found" errors
- "MountVolume.SetUp failed" errors

**Diagnosis:**
```bash
# List secrets in namespace
kubectl get secrets -n prod

# Check secret contents (keys only)
kubectl describe secret auth-secrets -n prod
```

**Solutions:**
```bash
# Recreate missing secret
kubectl delete secret auth-secrets -n prod
./scripts/manage-env.sh secrets prod auth JWT_SECRET new-secret-value

# Update deployment to use correct secret name
kubectl edit deployment auth -n prod
```

### Debugging Commands

```bash
# Get all environment variables for a deployment
kubectl get deployment auth -n dev -o jsonpath='{.spec.template.spec.containers[0].env[*]}' | jq

# Check if service is healthy
kubectl get pods -n dev -l app=auth

# View recent events
kubectl get events -n dev --sort-by=.metadata.creationTimestamp

# Check service logs
kubectl logs -f deployment/auth -n dev

# Execute commands inside pod
kubectl exec -it deployment/auth -n dev -- env | grep DATABASE
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
DEBUG="true|false"
```

### Useful Commands

```bash
# View all services and their environment variables
for svc in auth profile content notifications chat analytics content-worker; do
  echo "=== $svc ==="
  ./scripts/manage-env.sh list dev $svc
  echo ""
done

# Check all deployments status
kubectl get deployments -A

# Monitor deployment rollouts
watch kubectl get pods -n dev

# Get environment overview
./scripts/manage-env.sh show
```

### File Locations

```bash
# Helm values files
deploy/helm/[service]/values.yaml          # Base configuration
deploy/helm/[service]/values.dev.yaml      # Development overrides
deploy/helm/[service]/values.staging.yaml  # Staging overrides
deploy/helm/[service]/values.prod.yaml     # Production overrides

# Templates
deploy/helm/[service]/templates/deployment.yaml  # Kubernetes deployment template

# Scripts
scripts/manage-env.sh                      # Environment management script

# Documentation
ENV_REFERENCE.md                          # Complete variable reference
ENVIRONMENT_VARIABLES_GUIDE.md           # This guide
```

### Quick Setup Checklist

- [ ] Kubernetes cluster is running
- [ ] Helm is installed and configured
- [ ] `scripts/manage-env.sh` is executable
- [ ] Namespaces created (dev, staging, prod)
- [ ] Infrastructure services deployed (PostgreSQL, Redis, etc.)
- [ ] Environment variables configured in values files
- [ ] Secrets created for production environment
- [ ] Services deployed and healthy

---

## 💡 Pro Tips

1. **Always test environment changes in dev first**
2. **Use the management script for consistency**
3. **Keep production secrets separate and secure**
4. **Document any custom environment variables in ENV_REFERENCE.md**
5. **Use environment-specific values files for different configurations**
6. **Monitor deployment status after environment changes**
7. **Backup production secrets before rotation**
8. **Use meaningful names for environment variables**
9. **Group related variables together in values files**
10. **Test secret rotation in staging before production**

This guide provides everything you need to effectively manage environment variables in your AI project using Helm charts and Kubernetes secrets. For specific variable references, see `ENV_REFERENCE.md`.
