# VPS Deployment Guide

## Current Status
Your VPS is configured with:
- ✅ K3s (Kubernetes) cluster running
- ✅ Nginx Ingress Controller installed
- ✅ Firewall configured (ports 22, 80, 443, 6443)
- ✅ Docker registry credentials configured
- ❌ Services failing due to missing Docker images

## Issues to Fix

### 1. InvalidImageName Errors
Your pods are failing because the Docker images don't exist in the registry. The Helm templates are trying to use `ghcr.io/m1aso/SERVICE_NAME:DEV_SHA` but these images haven't been built.

### 2. Missing Docker Images
You need to build and push your Docker images to GitHub Container Registry (GHCR).

## Step-by-Step Deployment

### Step 1: Build and Push Docker Images

From your local machine (where you have Docker installed):

```bash
# 1. Login to GitHub Container Registry
docker login ghcr.io -u M1aso -p YOUR_GITHUB_TOKEN

# 2. Build and push all images
./build-and-push.sh latest

# Alternative: Build individual services
# docker build -t ghcr.io/m1aso/auth:latest services/auth
# docker push ghcr.io/m1aso/auth:latest
```

### Step 2: Copy Deployment Files to VPS

```bash
# Copy the project to your VPS
scp -r deploy/ root@45.146.164.70:/root/
scp deploy-to-vps.sh root@45.146.164.70:/root/
```

### Step 3: Deploy to VPS

SSH into your VPS and run:

```bash
ssh root@45.146.164.70

# Set up kubectl context
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Navigate to project directory
cd /root

# Make script executable
chmod +x deploy-to-vps.sh

# Deploy all services
./deploy-to-vps.sh
```

### Step 4: Verify Deployment

Check if all pods are running:
```bash
kubectl -n dev get pods
```

Test your endpoints:
```bash
curl -i http://45.146.164.70.nip.io/api/auth/healthz
curl -i http://45.146.164.70.nip.io/api/profile/healthz
```

## Alternative: Quick Fix for Current Deployment

If you want to quickly fix the current broken deployment without rebuilding images:

### Option A: Use existing Python base image temporarily

SSH to your VPS and run:

```bash
# Delete current broken deployments
kubectl -n dev delete deployment --all

# Deploy with a working base image for testing
helm upgrade --install auth deploy/helm/auth \
  --namespace dev \
  --set image.repository=python \
  --set image.tag=3.12-slim \
  --set imagePullSecrets=null
```

### Option B: Build images directly on VPS

```bash
# Install Docker on VPS
apt-get update && apt-get install -y docker.io
systemctl start docker
systemctl enable docker

# Clone your repository
git clone https://github.com/M1aso/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Build images locally on VPS
docker build -t ghcr.io/m1aso/auth:latest services/auth
# ... repeat for other services

# Or use the build script
./build-and-push.sh latest
```

## Dependencies to Deploy

Your services likely need these additional components:

### Redis (for chat service)
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis --namespace dev \
  --set auth.enabled=false \
  --set architecture=standalone
```

### MinIO (for profile service - file storage)
```bash
helm repo add minio https://charts.min.io/
helm install minio minio/minio --namespace dev \
  --set rootUser=admin \
  --set rootPassword=password123 \
  --set persistence.enabled=false
```

## Troubleshooting Commands

```bash
# Check pod status
kubectl -n dev get pods

# Check pod logs
kubectl -n dev logs -l app=auth

# Describe failing pod
kubectl -n dev describe pod POD_NAME

# Check ingress
kubectl -n ingress-nginx get svc

# Check if images exist
docker pull ghcr.io/m1aso/auth:latest

# Test internal service connectivity
kubectl -n dev run test-pod --image=curlimages/curl --rm -it -- sh
# Then inside pod: curl http://auth:8000/healthz
```

## Production Considerations

1. **Security**: Change default passwords and JWT secrets
2. **Persistence**: Configure persistent volumes for databases
3. **Monitoring**: Add Prometheus/Grafana for monitoring
4. **SSL**: Configure SSL certificates for HTTPS
5. **Backup**: Set up database backups
6. **Scaling**: Adjust resource limits based on usage

## Next Steps

1. Build and push your Docker images
2. Deploy using the production values
3. Set up monitoring and logging
4. Configure SSL certificates
5. Set up CI/CD pipeline for automated deployments

Your application will be available at: http://45.146.164.70.nip.io/api/SERVICE_NAME/