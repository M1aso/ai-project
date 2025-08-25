# Deployment Stability Fix

## Issue
Auth service deployments were getting stuck with "1 old replicas are pending termination" due to:
1. New images failing to start (database connectivity issues)
2. Health check failures causing restart loops
3. Kubernetes unable to terminate old pods when new ones fail

## Root Cause
Recent commits introduced breaking changes that prevented the auth service from starting:
- Database connection timeouts
- Missing environment variables
- Application startup failures

## Permanent Fix Implemented

### 1. Stable Image Pinning
- Auth service now uses stable image: `ghcr.io/m1aso/auth:b5eac45b352178ec63fdb603c58b74bfb270064e`
- This image is confirmed working with proper database connectivity
- Full SHA ensures exact image reproducibility

### 2. Deployment Strategy
- Use full SHA commits instead of short SHAs for image tags
- Implement health check grace periods for database connectivity
- Force cleanup of stuck pods during deployment issues

### 3. Monitoring & Rollback
- Monitor pod startup logs for early failure detection
- Automatic rollback to last known working image on failure
- Clear documentation of working image versions

## Current Status
✅ All services running (10/10):
- auth: 1/1 ready (stable image)
- profile: 1/1 ready
- content: 1/1 ready  
- content-worker: 1/1 ready
- All other services: healthy

## Next Steps
1. Test new commits in staging before production
2. Implement blue-green deployment for critical services
3. Add deployment health checks to CI pipeline
