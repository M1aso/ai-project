# 🚨 Critical Service Deployment Fix

## Current Issue
All services are returning 404 errors because:
1. **Services may not be deployed** - The API gateway configuration has been fixed but services need to be deployed
2. **Configuration not applied** - The updated API gateway configuration needs to be redeployed
3. **Route precedence issues** - Fixed in the configuration but needs deployment

## 🔧 Immediate Fix Steps

### Step 1: Deploy the Fixed API Gateway Configuration
```bash
# Deploy the updated API gateway with fixed routing
helm upgrade --install api-gateway deploy/helm/api-gateway \
  --namespace dev --create-namespace \
  -f deploy/helm/api-gateway/values.dev.yaml

# Wait for deployment
kubectl rollout status deployment/api-gateway -n dev
```

### Step 2: Deploy All Services
```bash
# Deploy all services to dev environment
services=("auth" "profile" "content" "notifications" "chat" "analytics")

for svc in "${services[@]}"; do
  echo "Deploying $svc..."
  helm upgrade --install "$svc" "deploy/helm/$svc" \
    --namespace dev --create-namespace \
    --set "image.repository=ghcr.io/m1aso/$svc" \
    --set "image.tag=latest" \
    -f "deploy/helm/$svc/values.dev.yaml"
done
```

### Step 3: Verify Deployment
```bash
# Check if all pods are running
kubectl get pods -n dev

# Check if all services are created
kubectl get services -n dev

# Test the API gateway
curl http://api.45.146.164.70.nip.io/
```

## 🔍 What Was Fixed

### 1. Envoy Route Configuration (`deploy/helm/api-gateway/templates/configmap.yaml`)
**Fixed route precedence issues:**
- ✅ Specific routes (e.g., `/api/content/healthz`) now come before general routes (`/api/content`)
- ✅ Added explicit health check routes for all services
- ✅ Added WebSocket support for chat service (`/ws`)
- ✅ Added catch-all route for root path (`/`) with service information

**Before (broken):**
```yaml
- match: { prefix: "/api/content" }
  route:
    cluster: "content_cluster"
    prefix_rewrite: "/"  # Wrong! This breaks routing
```

**After (fixed):**
```yaml
- match: { prefix: "/api/content/healthz" }  # Specific first
  route:
    cluster: "content_cluster"
    prefix_rewrite: "/api/content/healthz"
- match: { prefix: "/api/content" }         # General second
  route:
    cluster: "content_cluster"
    prefix_rewrite: "/api/content"
```

### 2. Service Cluster Definitions
**Fixed cluster configuration:**
- ✅ Explicit cluster definitions for all services
- ✅ Correct service names (`auth.dev.svc.cluster.local`)
- ✅ Standardized port 8000 for all services

### 3. Content Service Implementation (`services/content/cmd/server/main.go`)
**Added proper health endpoints:**
- ✅ Health check at `/healthz` (direct access)
- ✅ Health check at `/api/content/healthz` (through API path)
- ✅ Improved JSON responses with proper headers

## 🧪 Testing the Fix

### Test Script
Run the verification script:
```bash
./scripts/verify-services.sh dev
```

### Manual Testing
```bash
# Test API Gateway root
curl http://api.45.146.164.70.nip.io/
# Expected: {"status":"ok","message":"AI Project API Gateway",...}

# Test all health endpoints
curl http://api.45.146.164.70.nip.io/api/auth/healthz
curl http://api.45.146.164.70.nip.io/api/profile/healthz
curl http://api.45.146.164.70.nip.io/api/content/healthz
curl http://api.45.146.164.70.nip.io/api/notifications/healthz
curl http://api.45.146.164.70.nip.io/api/analytics/healthz

# Test functional endpoints
curl http://api.45.146.164.70.nip.io/api/content/courses
curl -X POST http://api.45.146.164.70.nip.io/api/auth/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567"}'
```

## 🔄 Automated Deployment via GitHub Actions

### Option 1: Push to dev branch (triggers auto-deployment)
```bash
git add .
git commit -m "fix: critical API gateway routing and service configuration"
git push origin dev
```

### Option 2: Manual deployment via GitHub Actions
1. Go to your repository on GitHub
2. Navigate to **Actions** tab
3. Select **Deploy** workflow
4. Click **Run workflow**
5. Choose:
   - **Environment**: `dev`
   - **Service**: Leave empty (deploys all services)

## 📋 Deployment Checklist

### Pre-deployment
- [x] Fixed Envoy route precedence in `configmap.yaml`
- [x] Added explicit cluster definitions for all services
- [x] Fixed content service health endpoints
- [x] Updated documentation with correct endpoints
- [x] Created verification script

### Post-deployment (verify these)
- [ ] API Gateway pod is running: `kubectl get pods -n dev | grep api-gateway`
- [ ] All service pods are running: `kubectl get pods -n dev`
- [ ] All services are accessible: `./scripts/verify-services.sh dev`
- [ ] Health checks return 200: Test all `/api/*/healthz` endpoints
- [ ] Functional endpoints work: Test courses, auth, etc.

## 🚨 If Services Still Don't Work After Deployment

### 1. Check Pod Status
```bash
kubectl get pods -n dev
kubectl describe pod <pod-name> -n dev
kubectl logs <pod-name> -n dev
```

### 2. Check Service Configuration
```bash
kubectl get services -n dev
kubectl describe service <service-name> -n dev
```

### 3. Check Ingress
```bash
kubectl get ingress -n dev
kubectl describe ingress api-gateway -n dev
```

### 4. Check API Gateway Logs
```bash
kubectl logs deployment/api-gateway -n dev
```

### 5. Test Direct Service Access (Bypass Gateway)
```bash
# Port-forward to test services directly
kubectl port-forward service/auth 8001:8000 -n dev &
curl http://localhost:8001/api/auth/healthz

kubectl port-forward service/content 8003:8000 -n dev &
curl http://localhost:8003/api/content/healthz
```

## 🎯 Expected Results After Fix

### ✅ Working Endpoints
```bash
# Root endpoint
curl http://api.45.146.164.70.nip.io/
# → {"status":"ok","message":"AI Project API Gateway","services":[...]}

# Health checks
curl http://api.45.146.164.70.nip.io/api/auth/healthz
# → {"status":"ok","service":"auth"}

curl http://api.45.146.164.70.nip.io/api/content/healthz
# → {"status":"ok","service":"content"}

# Functional endpoints
curl http://api.45.146.164.70.nip.io/api/content/courses
# → {"courses":[],"status":"ok"}

curl -X POST http://api.45.146.164.70.nip.io/api/auth/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567"}'
# → Should return proper error/success response, not 404
```

## 📞 Next Steps

1. **Deploy the fixes** using one of the deployment methods above
2. **Run the verification script** to confirm all services are working
3. **Update client applications** if needed with any endpoint changes
4. **Monitor logs** for any remaining issues

The root cause was a combination of:
- **Route precedence issues** in Envoy (fixed)
- **Missing/incorrect cluster definitions** (fixed)
- **Services potentially not deployed** (needs deployment)

Once deployed, all services should be accessible through the API gateway at the correct endpoints.
