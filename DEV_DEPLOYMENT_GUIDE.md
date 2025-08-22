# DEV Environment Deployment Guide

## 🎯 Your Dev Environment
- **VPS IP**: `45.146.164.70`
- **Domain**: `45.146.164.70.nip.io`
- **Environment**: Development
- **Kubernetes**: K3s cluster ready
- **Ingress**: Nginx controller configured

## 🚨 Current Issues
Your pods show `InvalidImageName` because they're trying to use `DEV_SHA` tag which doesn't exist. I've fixed your dev values to use proper image names.

## 🚀 Quick Solution (Run on VPS)

**Copy this script to your VPS and run it:**

```bash
# From your local machine:
scp quick-fix-vps.sh root@45.146.164.70:/root/

# SSH into VPS and run:
ssh root@45.146.164.70
chmod +x quick-fix-vps.sh
./quick-fix-vps.sh
```

This will:
1. ✅ Install Docker on VPS
2. ✅ Clone your repository 
3. ✅ Build all Docker images with `dev` tag
4. ✅ Deploy all services to dev namespace
5. ✅ Configure ingress routing

## 📋 What I Fixed

### 1. Updated Dev Values Files
- ✅ Fixed `auth/values.dev.yaml` - proper image repo and dev tag
- ✅ Fixed `profile/values.dev.yaml` - proper image repo and dev tag  
- ✅ Fixed `content/values.dev.yaml` - proper image repo and dev tag
- ✅ Fixed `chat/values.dev.yaml` - proper image repo and dev tag
- ✅ Fixed `notifications/values.dev.yaml` - proper image repo and dev tag
- ✅ Fixed `analytics/values.dev.yaml` - proper image repo and dev tag
- ✅ Fixed `content-worker/values.dev.yaml` - proper image repo and dev tag
- ✅ Updated all to use `ghcr-creds` secret name

### 2. Created Dev-Specific Scripts
- ✅ `deploy-dev.sh` - Deploy using dev values
- ✅ `quick-fix-vps.sh` - All-in-one fix for VPS
- ✅ `build-and-push.sh` - Build with dev tag by default

## 🔄 Alternative: Manual Steps

If you prefer to do it step by step:

### Step 1: Build Images (Local or VPS)

**Option A: Build locally and push**
```bash
# On your local machine:
docker login ghcr.io -u M1aso -p YOUR_GITHUB_TOKEN
./build-and-push.sh dev
```

**Option B: Build directly on VPS**
```bash
# SSH into VPS:
ssh root@45.146.164.70

# Install Docker and clone repo:
apt-get update && apt-get install -y docker.io git
systemctl start docker
git clone https://github.com/M1aso/microservices-platform.git
cd microservices-platform

# Build images:
docker build -t ghcr.io/m1aso/auth:dev services/auth
docker build -t ghcr.io/m1aso/profile:dev services/profile
docker build -t ghcr.io/m1aso/content:dev services/content
docker build -t ghcr.io/m1aso/chat:dev services/chat
docker build -t ghcr.io/m1aso/notifications:dev services/notifications
docker build -t ghcr.io/m1aso/analytics:dev services/analytics
docker build -t ghcr.io/m1aso/content-worker:dev services/content-worker
```

### Step 2: Deploy Services

```bash
# On VPS with kubectl configured:
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Clean up broken deployments:
kubectl -n dev delete deployment --all

# Deploy using dev values:
./deploy-dev.sh
```

## 🧪 Testing Your Dev Environment

After deployment, test these endpoints:

```bash
# Health checks:
curl http://45.146.164.70.nip.io/api/auth/healthz
curl http://45.146.164.70.nip.io/api/profile/healthz
curl http://45.146.164.70.nip.io/api/content/healthz

# API endpoints (example):
curl http://45.146.164.70.nip.io/api/auth/users
curl http://45.146.164.70.nip.io/api/profile/me
```

## 🔍 Monitoring Commands

```bash
# Check all pods in dev namespace:
kubectl -n dev get pods

# Watch pods status in real-time:
kubectl -n dev get pods -w

# Check specific service logs:
kubectl -n dev logs -l app=auth
kubectl -n dev logs -l app=profile

# Check ingress status:
kubectl -n ingress-nginx get svc

# Test internal connectivity:
kubectl -n dev run debug --image=curlimages/curl --rm -it -- sh
# Inside pod: curl http://auth:8000/healthz
```

## 🎯 Next Steps for Dev Environment

1. **Deploy dependencies** (Redis, MinIO if needed)
2. **Set up development databases**
3. **Configure environment variables**
4. **Set up logging and monitoring**
5. **Test all API endpoints**

## 🚀 Quick Start

**Run this single command on your VPS:**
```bash
curl -sSL https://raw.githubusercontent.com/M1aso/microservices-platform/main/quick-fix-vps.sh | bash
```

Your dev environment will be ready at: **http://45.146.164.70.nip.io**