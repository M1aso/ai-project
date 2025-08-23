# 🚀 Restart All Services - Complete Fix

## 🎉 SUCCESS: API Gateway is Working!

✅ **Root endpoint working**: `http://api.45.146.164.70.nip.io/` returns proper JSON  
✅ **Envoy routing working**: Requests show `x-envoy-upstream-service-time` headers  
❌ **Individual services need deployment/restart**: Getting `{"detail":"Not Found"}`

## 🔄 Restart All Services (Run on Server)

### Step 1: Restart All Service Deployments
```bash
# Restart all microservices
services=("auth" "profile" "content" "notifications" "chat" "analytics" "content-worker")

for svc in "${services[@]}"; do
  echo "Restarting $svc..."
  kubectl rollout restart deployment/$svc -n dev
done

# Wait for all deployments to be ready
kubectl rollout status deployment/auth -n dev
kubectl rollout status deployment/profile -n dev  
kubectl rollout status deployment/content -n dev
kubectl rollout status deployment/notifications -n dev
kubectl rollout status deployment/chat -n dev
kubectl rollout status deployment/analytics -n dev
```

### Step 2: Verify All Pods are Running
```bash
kubectl get pods -n dev
```

### Step 3: Test Services After Restart
```bash
# Wait for services to be ready
sleep 30

# Test all health endpoints
curl http://api.45.146.164.70.nip.io/api/auth/healthz
curl http://api.45.146.164.70.nip.io/api/profile/healthz
curl http://api.45.146.164.70.nip.io/api/content/healthz
curl http://api.45.146.164.70.nip.io/api/notifications/healthz
curl http://api.45.146.164.70.nip.io/api/analytics/healthz
```

## 🧪 Alternative: Deploy Services if Not Exist

If services don't exist, deploy them:

```bash
# Deploy all services
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

## 📊 Expected Results

### ✅ After Service Restart/Deployment:

```bash
# All health endpoints should work
curl http://api.45.146.164.70.nip.io/api/auth/healthz
# → {"status":"ok","service":"auth"}

curl http://api.45.146.164.70.nip.io/api/content/healthz  
# → {"status":"ok","service":"content"}

curl http://api.45.146.164.70.nip.io/api/content/courses
# → {"courses":[],"status":"ok"}
```

### ✅ Verification Script Should Pass:
```bash
./scripts/verify-services.sh dev
# → Should show all services responding through API Gateway
```

## 🎯 Root Cause Analysis

The issue was a **two-part problem**:

1. **Root Ingress Missing**: Fixed ✅
   - GitHub Actions wasn't deploying `deploy/k8s/root-ingress.yaml`
   - Manual deployment resolved this

2. **API Gateway Stale Config**: Fixed ✅  
   - 3-hour-old logs indicated pod wasn't restarted with new config
   - `kubectl rollout restart` resolved this

3. **Individual Services**: Needs fixing 🔄
   - Services may not be deployed or have stale configurations
   - Restart/redeploy will resolve this

## 📋 Status Summary

- ✅ **API Gateway**: Working perfectly
- ✅ **Root Ingress**: Deployed and routing correctly  
- ✅ **Envoy Configuration**: Proper routing with headers
- 🔄 **Individual Services**: Need restart/deployment

**Run the service restart commands above to complete the fix!**
