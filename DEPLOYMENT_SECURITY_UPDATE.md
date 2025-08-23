# Security Update Deployment Guide

## Overview

This guide covers the deployment of critical security updates to the authentication service, including:
- bcrypt password hashing (replacing SHA-256)
- JWT token implementation
- Redis-backed rate limiting and session management
- Enhanced input validation
- Security headers and middleware

## Prerequisites

1. **Redis must be available** in the Kubernetes cluster
2. **Database migrations** need to be run (existing password hashes will need migration)
3. **Environment secrets** need to be updated for production

## Deployment Steps

### 1. Deploy Redis (if not already available)

```bash
# Deploy Redis to the cluster
kubectl apply -f deploy/k8s/redis-deployment.yaml

# Verify Redis is running
kubectl get pods -n redis
kubectl logs -n redis deployment/redis-master
```

### 2. Update Production Secrets

For production deployment, create the required secrets:

```bash
# Generate a strong JWT secret
JWT_SECRET=$(openssl rand -base64 32)

# Create or update the auth-secrets
kubectl create secret generic auth-secrets \
  --namespace=prod \
  --from-literal=database-url="postgresql://user:password@host:5432/dbname" \
  --from-literal=jwt-secret-key="$JWT_SECRET" \
  --from-literal=redis-password="your-redis-password" \
  --from-literal=allowed-origins="https://yourdomain.com,https://app.yourdomain.com" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 3. Deploy to Development

```bash
# Deploy only the auth service to dev
gh workflow run deploy.yml \
  --field environment=dev \
  --field service=auth

# Or deploy all services
gh workflow run deploy.yml \
  --field environment=dev
```

### 4. Verify Development Deployment

```bash
# Check pod status
kubectl get pods -n dev | grep auth

# Check logs for any errors
kubectl logs -n dev deployment/auth --tail=50

# Test the new endpoints
curl -X GET https://dev.yourdomain.com/api/auth/health
```

### 5. Test Security Features

#### Test Rate Limiting
```bash
# Test login rate limiting (should get 429 after 5 attempts)
for i in {1..10}; do
  curl -X POST https://dev.yourdomain.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrongpassword"}'
done
```

#### Test Password Validation
```bash
# Test weak password rejection
curl -X POST https://dev.yourdomain.com/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

#### Test JWT Authentication
```bash
# Register a user
curl -X POST https://dev.yourdomain.com/api/auth/email/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}'

# Login and get JWT token
response=$(curl -X POST https://dev.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123!"}')

# Extract access token and test protected endpoint
access_token=$(echo $response | jq -r '.access_token')
curl -X GET https://dev.yourdomain.com/api/auth/profile \
  -H "Authorization: Bearer $access_token"
```

### 6. Deploy to Staging

```bash
# Deploy to staging for final testing
gh workflow run deploy.yml \
  --field environment=staging \
  --field service=auth
```

### 7. Deploy to Production

⚠️ **CRITICAL: Password Migration Required**

Before deploying to production, you need to handle existing user passwords:

#### Option A: Force Password Reset (Recommended)
1. Deploy the new service
2. Send password reset emails to all users
3. Users reset passwords with new bcrypt hashing

#### Option B: Hybrid Validation (Advanced)
Implement temporary dual validation:
```python
def verify_password_hybrid(password: str, stored_hash: str) -> bool:
    """Temporary hybrid validation during migration."""
    # Try new bcrypt first
    if stored_hash.startswith('$2b$'):
        return pwd_context.verify(password, stored_hash)
    
    # Fall back to old SHA-256 and upgrade
    if hashlib.sha256(password.encode()).hexdigest() == stored_hash:
        # Password is correct, upgrade to bcrypt
        new_hash = pwd_context.hash(password)
        # Update database with new hash
        update_user_password_hash(user_id, new_hash)
        return True
    
    return False
```

#### Production Deployment
```bash
# Create production secrets first (see step 2)

# Deploy to production
gh workflow run deploy.yml \
  --field environment=prod \
  --field service=auth

# Monitor deployment
kubectl rollout status deployment/auth -n prod
kubectl get pods -n prod | grep auth
kubectl logs -n prod deployment/auth --tail=100
```

## Post-Deployment Verification

### 1. Health Checks
```bash
# Check service health
curl -X GET https://yourdomain.com/api/auth/healthz

# Check security headers
curl -I https://yourdomain.com/api/auth/healthz
```

### 2. Monitor Logs
```bash
# Monitor authentication attempts
kubectl logs -n prod deployment/auth -f | grep -E "(login|register|rate_limit)"

# Check for any errors
kubectl logs -n prod deployment/auth -f | grep -i error
```

### 3. Test Critical Flows
- User registration with strong password
- Email verification
- Login with session management
- Password reset flow
- Rate limiting behavior
- JWT token validation

## Monitoring and Alerting

### Key Metrics to Watch
1. **Failed login attempts** - Should be limited by rate limiting
2. **Password validation failures** - Users may struggle with new requirements
3. **JWT validation errors** - Could indicate token issues
4. **Redis connectivity** - Critical for rate limiting and sessions
5. **Response times** - bcrypt is more CPU intensive than SHA-256

### Recommended Alerts
```yaml
# Example Prometheus alerts
- alert: AuthHighFailedLogins
  expr: rate(auth_login_failures_total[5m]) > 10
  for: 2m
  annotations:
    summary: "High rate of failed login attempts"

- alert: AuthRedisDown
  expr: up{job="redis"} == 0
  for: 1m
  annotations:
    summary: "Redis is down - rate limiting and sessions affected"

- alert: AuthHighLatency
  expr: histogram_quantile(0.95, rate(auth_request_latency_seconds_bucket[5m])) > 2
  for: 5m
  annotations:
    summary: "Auth service high latency"
```

## Rollback Plan

If issues occur, rollback steps:

### 1. Quick Rollback
```bash
# Rollback to previous version
kubectl rollout undo deployment/auth -n prod

# Or deploy specific previous version
gh workflow run deploy.yml \
  --field environment=prod \
  --field service=auth
  # (with previous image tag)
```

### 2. Database Rollback (if needed)
```bash
# If database migrations were applied, may need to rollback
cd services/auth
alembic downgrade -1  # or to specific revision
```

### 3. Configuration Rollback
```bash
# Revert to previous Helm values if needed
git revert <security-update-commit>
gh workflow run deploy.yml --field environment=prod --field service=auth
```

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**
   ```bash
   # Check Redis status
   kubectl get pods -n redis
   kubectl logs -n redis deployment/redis-master
   
   # Test Redis connectivity from auth pod
   kubectl exec -it -n prod deployment/auth -- redis-cli -h redis-master.redis.svc.cluster.local ping
   ```

2. **JWT Secret Mismatch**
   ```bash
   # Check secret exists
   kubectl get secret auth-secrets -n prod
   kubectl describe secret auth-secrets -n prod
   
   # Verify JWT_SECRET_KEY is set correctly
   kubectl exec -it -n prod deployment/auth -- env | grep JWT
   ```

3. **Database Migration Issues**
   ```bash
   # Check current migration status
   kubectl exec -it -n prod deployment/auth -- alembic current
   
   # Run migrations if needed
   kubectl exec -it -n prod deployment/auth -- alembic upgrade head
   ```

4. **Password Validation Too Strict**
   - Temporarily reduce password requirements in validators.py
   - Redeploy with relaxed validation
   - Gradually increase requirements

## Security Considerations

### Production Checklist
- [ ] Strong JWT secret generated and stored securely
- [ ] Redis password configured (if using authentication)
- [ ] Database connections use SSL
- [ ] CORS origins configured correctly
- [ ] Rate limiting thresholds appropriate for traffic
- [ ] Monitoring and alerting configured
- [ ] Backup and disaster recovery tested
- [ ] Security headers validated
- [ ] Password migration strategy implemented

### Ongoing Security Tasks
- [ ] Regular JWT secret rotation (quarterly)
- [ ] Monitor for security vulnerabilities in dependencies
- [ ] Review and update rate limiting thresholds
- [ ] Audit authentication logs regularly
- [ ] Test disaster recovery procedures
- [ ] Update security documentation

## Success Criteria

Deployment is successful when:
1. ✅ All pods are running and healthy
2. ✅ Health checks pass
3. ✅ User registration works with strong passwords
4. ✅ Login returns JWT tokens
5. ✅ Rate limiting prevents brute force attacks
6. ✅ Session management works correctly
7. ✅ Password reset flow functions
8. ✅ No critical errors in logs
9. ✅ Performance is acceptable
10. ✅ Monitoring shows normal metrics
