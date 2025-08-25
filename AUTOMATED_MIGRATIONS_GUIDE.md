# 🚀 Automated Database Migrations Guide

## Overview
This guide explains how to implement automated database migrations for all services in your AI Project, ensuring database schemas are always up-to-date with code deployments.

## 🎯 **Migration Strategies**

### **Strategy 1: Helm Pre-Hook Migration Jobs (Recommended)**

**How it works:**
- Migration job runs **before** service deployment
- Uses Helm hooks (`pre-install`, `pre-upgrade`)
- Ensures database is ready before service starts
- Automatic cleanup after successful migration

**Benefits:**
- ✅ **Zero downtime** - migrations complete before service starts
- ✅ **Automatic** - no manual intervention needed
- ✅ **Safe** - service won't start if migration fails
- ✅ **Auditable** - migration logs in Kubernetes

**Implementation:**
```yaml
# In values.yaml
migrations:
  enabled: true
  timeout: 300
  retries: 3
  waitForDatabase: true
```

### **Strategy 2: Application Startup Migration**

**How it works:**
- Service runs migrations on startup
- Built into application lifecycle
- Waits for database readiness

**Benefits:**
- ✅ **Simple** - no additional Kubernetes resources
- ✅ **Flexible** - can handle complex migration logic
- ✅ **Integrated** - part of application startup

**Implementation:**
```python
# In main.py lifespan function
if os.getenv("RUN_MIGRATIONS", "true").lower() == "true":
    if wait_for_database():
        run_migrations()
```

### **Strategy 3: Init Container Migration**

**How it works:**
- Init container runs before main service
- Blocks service until migration completes
- Shares same image as main service

**Benefits:**
- ✅ **Guaranteed** - service won't start without migration
- ✅ **Efficient** - reuses service image
- ✅ **Kubernetes native** - uses init container pattern

## 🔧 **Implementation Steps**

### **Step 1: Update Helm Values**

Add migration configuration to each service:

```yaml
# services/auth/values.yaml
migrations:
  enabled: true
  timeout: 300
  retries: 3
  waitForDatabase: true
  
  # Optional: Custom migration command
  command: "alembic upgrade head"
  
  # Optional: Custom environment variables
  env:
    - name: CUSTOM_MIGRATION_VAR
      value: "value"
```

### **Step 2: Create Migration Templates**

Each service gets a migration job template:

```yaml
# services/auth/templates/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "svc.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
```

### **Step 3: Update Application Code**

Add migration logic to service startup:

```python
# In main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Wait for database and run migrations
    if os.getenv("RUN_MIGRATIONS", "true").lower() == "true":
        if wait_for_database():
            run_migrations()
    
    yield
```

## 📋 **Service-Specific Configurations**

### **Python Services (FastAPI/Django)**

```yaml
# services/auth/values.yaml
migrations:
  enabled: true
  command: "alembic upgrade head"
  env:
    - name: PYTHONPATH
      value: "/app"
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: auth-db-secret
          key: url
```

### **Go Services**

```yaml
# services/content/values.yaml
migrations:
  enabled: true
  command: "go run cmd/migrate/main.go"
  env:
    - name: DB_HOST
      value: "postgresql.postgresql.svc.cluster.local"
```

### **Node.js Services**

```yaml
# services/chat/values.yaml
migrations:
  enabled: true
  command: "npm run migrate"
  env:
    - name: NODE_ENV
      value: "production"
```

## 🚨 **Migration Safety Features**

### **1. Database Readiness Check**

```python
def wait_for_database():
    max_retries = 30
    retry_delay = 2
    
    for i in range(max_retries):
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            db.close()
            return True
        except Exception:
            if i < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return False
```

### **2. Migration Timeout**

```python
def run_migrations():
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            timeout=300  # 5 minutes
        )
    except subprocess.TimeoutExpired:
        print("Migration timeout - continuing without migration")
```

### **3. Rollback Support**

```yaml
# In migration job
spec:
  template:
    spec:
      restartPolicy: Never
      backoffLimit: 3  # Retry failed migrations
```

## 🔍 **Monitoring & Debugging**

### **1. Check Migration Status**

```bash
# View migration jobs
kubectl get jobs -n dev | grep migration

# Check migration logs
kubectl logs -n dev job/auth-migration-abc123
```

### **2. Migration History**

```bash
# Check database migration status
kubectl exec -it -n dev auth-pod -- alembic current
kubectl exec -it -n dev auth-pod -- alembic history
```

### **3. Troubleshooting**

```bash
# Check if migration job exists
kubectl get job -n dev auth-migration

# Describe migration job
kubectl describe job -n dev auth-migration

# Check service startup logs
kubectl logs -n dev auth-pod --tail=50
```

## 📊 **Environment-Specific Configurations**

### **Development Environment**

```yaml
# values.dev.yaml
migrations:
  enabled: true
  timeout: 300
  retries: 3
  waitForDatabase: true
  env:
    - name: DEBUG
      value: "true"
```

### **Production Environment**

```yaml
# values.prod.yaml
migrations:
  enabled: true
  timeout: 600  # Longer timeout for production
  retries: 5
  waitForDatabase: true
  env:
    - name: DEBUG
      value: "false"
```

## 🎯 **Best Practices**

### **1. Migration Order**
- Run migrations **before** service deployment
- Use Helm hook weights to control order
- Ensure database dependencies are ready

### **2. Error Handling**
- Graceful fallback if migrations fail
- Clear error messages and logging
- Automatic retry with exponential backoff

### **3. Security**
- Use service accounts with minimal permissions
- Store sensitive data in Kubernetes secrets
- Validate migration scripts before deployment

### **4. Testing**
- Test migrations in development first
- Use database snapshots for testing
- Validate migration rollbacks

## 🚀 **Next Steps**

1. **Implement Strategy 1** (Helm pre-hook) for auth service
2. **Test the migration flow** in development
3. **Apply to other services** (profile, content, notifications)
4. **Set up monitoring** for migration success/failure
5. **Document migration procedures** for team

## 📚 **Related Files**

- `deploy/helm/auth/templates/migration-job.yaml` - Auth service migration
- `deploy/helm/_templates/migration-job.yaml` - Reusable template
- `services/auth/app/main.py` - Application startup migration
- `AUTH_TESTING_GUIDE.md` - Testing guide
- `RATE_LIMITING_CONFIG.md` - Rate limiting configuration

---

**Automated migrations ensure your database schema is always in sync with your code, eliminating deployment issues and manual intervention! 🎉**
