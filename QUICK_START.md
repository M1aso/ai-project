# Quick Start Guide

## 🚀 Get Your AI Project Running in 15 Minutes

### Prerequisites
- VPS: 45.146.164.70 (Ubuntu 20.04+)
- GitHub repository: https://github.com/M1aso/ai-project
- GitHub account with admin access

### Step 1: VPS Setup (5 minutes)

SSH into your VPS and run the automated setup script:

```bash
# SSH into your VPS
ssh root@45.146.164.70

# Create a user (if not exists)
adduser aiproject
usermod -aG sudo aiproject
su - aiproject

# Clone repository and run setup
git clone https://github.com/M1aso/ai-project.git
cd ai-project
chmod +x scripts/setup-vps.sh
./scripts/setup-vps.sh dev
```

**This script will install:**
- Docker & Docker Compose
- Kubernetes (k3s)
- Helm
- NGINX Ingress Controller
- PostgreSQL, Redis, RabbitMQ, MinIO
- Prometheus & Grafana

### Step 2: GitHub Secrets Setup (3 minutes)

1. **Create GitHub Personal Access Token:**
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Create token with `packages:write` and `repo` permissions
   - Copy the token

2. **Add Repository Secrets:**
   - Go to your repo: Settings > Secrets and variables > Actions
   - Add these **Repository secrets**:
     - `GHCR_USERNAME`: `M1aso`
     - `GHCR_TOKEN`: `<your-github-token>`

3. **Add Environment Secrets:**
   - Go to Settings > Environments
   - Create environment `dev`
   - Add **Environment secret**:
     - `KUBE_CONFIG`: Run this on your VPS and copy the output:
       ```bash
       sudo cat /etc/rancher/k3s/k3s.yaml | sed 's/127.0.0.1/45.146.164.70/g' | base64 -w 0
       ```

### Step 3: Deploy Application (2 minutes)

```bash
# Create and push dev branch
git checkout -b dev
git push origin dev

# This will automatically trigger deployment via GitHub Actions!
```

### Step 4: Access Your Services (1 minute)

After deployment completes (~3-5 minutes), access your services:

| Service | URL | Credentials |
|---------|-----|-------------|
| **🌐 API Gateway** | http://api.45.146.164.70.nip.io | - |
| **📚 API Docs (Swagger)** | http://docs.45.146.164.70.nip.io | - |
| **📊 Grafana** | http://grafana.45.146.164.70.nip.io | admin / admin123 |
| **💾 MinIO Console** | http://minio.45.146.164.70.nip.io | admin / admin123456 |
| **🐰 RabbitMQ** | http://rabbitmq.45.146.164.70.nip.io | admin / admin123 |
| **📈 Prometheus** | http://prometheus.45.146.164.70.nip.io | - |

### Step 5: Test Your API (2 minutes)

```bash
# Test health endpoints
curl http://api.45.146.164.70.nip.io/api/auth/healthz
curl http://api.45.146.164.70.nip.io/api/profile/healthz
curl http://api.45.146.164.70.nip.io/api/content/healthz
curl http://api.45.146.164.70.nip.io/api/notifications/healthz
curl http://api.45.146.164.70.nip.io/api/analytics/healthz

# Test authentication (example)
curl -X POST http://api.45.146.164.70.nip.io/api/auth/phone/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79001234567"}'

# Test content service
curl http://api.45.146.164.70.nip.io/api/content/courses
```

## 🔄 Development Workflow

### Making Changes:
```bash
# Create feature branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/my-new-feature

# Make your changes
# ... edit code ...

# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-new-feature

# Create PR to dev branch
# After merge → automatic deployment to dev environment!
```

### Deploying to Production:
```bash
# Merge dev to main
git checkout main
git merge dev
git push origin main

# Create release tag
git tag release-1.0.0
git push origin release-1.0.0

# This triggers automatic production deployment
```

## 🛠️ Common Operations

### View Logs:
```bash
kubectl logs -f deployment/auth -n dev
```

### Scale Services:
```bash
kubectl scale deployment auth --replicas=3 -n dev
```

### Update Environment Variables:
```bash
# Edit values file
vim deploy/helm/auth/values.dev.yaml

# Redeploy
helm upgrade auth deploy/helm/auth -n dev -f deploy/helm/auth/values.dev.yaml
```

### Manual Deployment:
```bash
# Deploy specific service
helm upgrade --install auth deploy/helm/auth \
  --namespace dev \
  -f deploy/helm/auth/values.dev.yaml \
  --set image.tag=latest
```

## 🆘 Troubleshooting

### Check Service Status:
```bash
kubectl get pods -A
kubectl get svc -A
kubectl get ingress -A
```

### Debug Pod Issues:
```bash
kubectl describe pod <pod-name> -n dev
kubectl logs <pod-name> -n dev
```

### Test Internal Connectivity:
```bash
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://auth.dev.svc.cluster.local:8000/healthz
```

## 📖 Full Documentation

For detailed information, see:
- **DEPLOYMENT.md**: Complete deployment guide
- **REQUIREMENTS.md**: Project requirements and architecture
- **libs/contracts/**: OpenAPI specifications

## 🎯 Success Indicators

✅ All pods running: `kubectl get pods -A`  
✅ API responding: `curl http://api.45.146.164.70.nip.io/api/auth/healthz`  
✅ Swagger UI accessible: http://docs.45.146.164.70.nip.io  
✅ Monitoring working: http://grafana.45.146.164.70.nip.io  
✅ Storage ready: http://minio.45.146.164.70.nip.io  

**🎉 Your AI E-Learning Platform is now live!**