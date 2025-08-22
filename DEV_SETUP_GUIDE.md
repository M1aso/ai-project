# AI Project - Dev Environment CI/CD Setup

## 🎯 Overview
- **Repository**: https://github.com/M1aso/ai-project
- **Dev VPS**: 45.146.164.70
- **Environment**: Development
- **CI/CD**: GitHub Actions → VPS Kubernetes

## 🚀 Quick Setup (3 Steps)

### Step 1: Prepare VPS
```bash
# Copy setup script to VPS
scp setup-vps.sh root@45.146.164.70:/root/

# SSH into VPS and run setup
ssh root@45.146.164.70
chmod +x setup-vps.sh
./setup-vps.sh
```

### Step 2: Configure GitHub Actions Access
```bash
# On your local machine, run:
./setup-vps-access.sh
```
Follow the instructions to:
- Generate SSH keys
- Add public key to VPS
- Add secrets to GitHub repository

### Step 3: Deploy
```bash
# Push code to trigger deployment
git push origin main

# Or manually trigger deployment
# Go to: https://github.com/M1aso/ai-project/actions
# Click "Deploy to Dev" → "Run workflow"
```

## 📋 Required GitHub Secrets

Add these in GitHub → Settings → Secrets and variables → Actions:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `SSH_HOST` | `45.146.164.70` | VPS IP address |
| `SSH_USERNAME` | `root` | VPS username |
| `SSH_PRIVATE_KEY` | `(private key content)` | SSH private key for VPS access |
| `KUBE_CONFIG` | `(base64 encoded)` | Kubernetes config from VPS |

## 🔄 CI/CD Workflow

The GitHub Actions workflow will:

1. **Build Phase**:
   - Build Docker images for all services
   - Push to GitHub Container Registry (GHCR)
   - Tag with commit SHA and 'dev'

2. **Deploy Phase**:
   - Connect to VPS via SSH
   - Deploy using Helm charts
   - Update services with new images
   - Verify deployment

3. **Test Phase**:
   - Health check all endpoints
   - Verify services are running

## 🌐 Access Your Dev Environment

After deployment, your services will be available at:

- **Main API**: http://45.146.164.70.nip.io/api/
- **Auth Service**: http://45.146.164.70.nip.io/api/auth/healthz
- **Profile Service**: http://45.146.164.70.nip.io/api/profile/healthz
- **Content Service**: http://45.146.164.70.nip.io/api/content/healthz
- **Chat Service**: http://45.146.164.70.nip.io/api/chat/healthz
- **Notifications**: http://45.146.164.70.nip.io/api/notifications/healthz
- **Analytics**: http://45.146.164.70.nip.io/api/analytics/healthz

## 🔍 Monitoring Commands

```bash
# SSH into VPS
ssh root@45.146.164.70

# Check all pods
kubectl -n dev get pods

# Check specific service logs
kubectl -n dev logs -l app=auth

# Watch deployment status
kubectl -n dev get pods -w

# Check ingress status
kubectl -n ingress-nginx get svc
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Pods stuck in ImagePullBackOff**:
   ```bash
   # Check if images exist
   kubectl -n dev describe pod POD_NAME
   
   # Verify GHCR credentials
   kubectl -n dev get secret ghcr-creds
   ```

2. **Services not accessible**:
   ```bash
   # Check ingress controller
   kubectl -n ingress-nginx get pods
   
   # Check service endpoints
   kubectl -n dev get endpoints
   ```

3. **Build failures**:
   - Check GitHub Actions logs
   - Verify Docker builds locally: `docker build services/auth`

## 🔄 Development Workflow

1. **Make changes** to your code
2. **Commit and push** to main branch
3. **GitHub Actions** automatically builds and deploys
4. **Test** your changes at http://45.146.164.70.nip.io
5. **Monitor** via kubectl commands

## 📱 Quick Commands

```bash
# Trigger manual deployment
gh workflow run deploy-dev.yml

# Check deployment status
kubectl -n dev get pods

# Test endpoints
curl http://45.146.164.70.nip.io/api/auth/healthz

# View logs
kubectl -n dev logs -l app=auth --tail=100
```

Your dev environment will automatically update every time you push to the main branch! 🚀