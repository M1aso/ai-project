# VPS Deployment Guide

## VPS Information
- **Dev Environment**: 45.146.164.70
- **Production**: TBD (will be configured later)

## 1. VPS Initial Setup

### 1.1. System Requirements
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git vim htop unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

### 1.2. Install Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### 1.3. Install Kubernetes (k3s)
```bash
# Install k3s (lightweight Kubernetes)
curl -sfL https://get.k3s.io | sh -

# Configure kubectl for current user
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
export KUBECONFIG=~/.kube/config

# Verify installation
kubectl get nodes
```

### 1.4. Install Helm
```bash
# Install Helm
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt update
sudo apt install -y helm

# Verify installation
helm version
```

### 1.5. Install NGINX Ingress Controller
```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for deployment
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

## 2. Infrastructure Services Setup

### 2.1. Install MinIO (Object Storage)
```bash
# Create MinIO namespace and deployment
kubectl create namespace minio

# Create MinIO deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio:latest
        command: ["minio", "server", "/data", "--console-address", ":9001"]
        env:
        - name: MINIO_ROOT_USER
          value: "admin"
        - name: MINIO_ROOT_PASSWORD
          value: "admin123456"
        ports:
        - containerPort: 9000
        - containerPort: 9001
        volumeMounts:
        - name: minio-storage
          mountPath: /data
      volumes:
      - name: minio-storage
        hostPath:
          path: /opt/minio-data
          type: DirectoryOrCreate
---
apiVersion: v1
kind: Service
metadata:
  name: minio
  namespace: minio
spec:
  selector:
    app: minio
  ports:
  - name: api
    port: 9000
    targetPort: 9000
  - name: console
    port: 9001
    targetPort: 9001
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: minio-ingress
  namespace: minio
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "0"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
spec:
  ingressClassName: nginx
  rules:
  - host: minio.45.146.164.70.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: minio
            port:
              number: 9001
  - host: minio-api.45.146.164.70.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: minio
            port:
              number: 9000
EOF
```

### 2.2. Install PostgreSQL
```bash
# Add PostgreSQL Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install PostgreSQL
helm install postgresql bitnami/postgresql \
  --namespace postgresql \
  --create-namespace \
  --set auth.postgresPassword=postgres123 \
  --set auth.database=aiproject \
  --set primary.persistence.size=10Gi

# Get PostgreSQL password
export POSTGRES_PASSWORD=$(kubectl get secret --namespace postgresql postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
echo "PostgreSQL Password: $POSTGRES_PASSWORD"
```

### 2.3. Install Redis
```bash
# Install Redis
helm install redis bitnami/redis \
  --namespace redis \
  --create-namespace \
  --set auth.enabled=false \
  --set master.persistence.size=5Gi

# Verify Redis installation
kubectl get pods -n redis
```

### 2.4. Install RabbitMQ
```bash
# Install RabbitMQ
helm install rabbitmq bitnami/rabbitmq \
  --namespace rabbitmq \
  --create-namespace \
  --set auth.username=admin \
  --set auth.password=admin123 \
  --set service.type=ClusterIP

# Create RabbitMQ ingress for management UI
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rabbitmq-ingress
  namespace: rabbitmq
spec:
  ingressClassName: nginx
  rules:
  - host: rabbitmq.45.146.164.70.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rabbitmq
            port:
              number: 15672
EOF
```

### 2.5. Install Prometheus & Grafana
```bash
# Add Prometheus community Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack (includes Grafana)
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin123 \
  --set grafana.service.type=ClusterIP \
  --set prometheus.service.type=ClusterIP

# Create Grafana ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: monitoring
spec:
  ingressClassName: nginx
  rules:
  - host: grafana.45.146.164.70.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: monitoring-grafana
            port:
              number: 80
EOF

# Create Prometheus ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prometheus-ingress
  namespace: monitoring
spec:
  ingressClassName: nginx
  rules:
  - host: prometheus.45.146.164.70.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: monitoring-kube-prometheus-prometheus
            port:
              number: 9090
EOF
```

## 3. Application Deployment

### 3.1. Create Namespaces
```bash
kubectl apply -f deploy/k8s/namespaces.yaml
```

### 3.2. Setup GitHub Container Registry Access
```bash
# Create GHCR secret for pulling images
kubectl create secret docker-registry ghcr \
  --docker-server=ghcr.io \
  --docker-username=M1aso \
  --docker-password=<YOUR_GITHUB_TOKEN> \
  --namespace=dev

# Copy to other namespaces
kubectl get secret ghcr --namespace=dev -o yaml | \
  sed 's/namespace: dev/namespace: staging/' | \
  kubectl apply -f -

kubectl get secret ghcr --namespace=dev -o yaml | \
  sed 's/namespace: dev/namespace: prod/' | \
  kubectl apply -f -
```

### 3.3. Deploy Application (Manual)
```bash
# Deploy API Gateway
helm upgrade --install api-gateway deploy/helm/api-gateway \
  --namespace dev \
  -f deploy/helm/api-gateway/values.dev.yaml

# Deploy all services
for svc in auth profile content notifications chat analytics content-worker; do
  helm upgrade --install "$svc" "deploy/helm/$svc" \
    --namespace dev \
    -f "deploy/helm/$svc/values.dev.yaml" \
    --set "image.repository=ghcr.io/m1aso/$svc" \
    --set "image.tag=dev"
done
```

## 4. Service Endpoints

### 4.1. Main Application Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| **API Gateway** | http://api.45.146.164.70.nip.io | Main API entry point |
| **Auth API** | http://api.45.146.164.70.nip.io/api/auth | Authentication endpoints |
| **Profile API** | http://api.45.146.164.70.nip.io/api/profile | User profile management |
| **Content API** | http://api.45.146.164.70.nip.io/api/content | Course content management |
| **Notifications API** | http://api.45.146.164.70.nip.io/api/notifications | Notification service |
| **Chat API** | http://api.45.146.164.70.nip.io/api/chat | Chat and messaging |
| **Analytics API** | http://api.45.146.164.70.nip.io/api/analytics | Analytics and reporting |

### 4.2. API Documentation (Swagger/OpenAPI)

The OpenAPI specifications are available in the `libs/contracts/` directory:
- **Auth API Spec**: `libs/contracts/auth.yaml`
- **Profile API Spec**: `libs/contracts/profile.yaml`
- **Content API Spec**: `libs/contracts/content.yaml`
- **Notifications API Spec**: `libs/contracts/notifications.yaml`
- **Chat API Spec**: `libs/contracts/chat.yaml`
- **Analytics API Spec**: `libs/contracts/analytics.yaml`

To serve Swagger UI, you can use:
```bash
# Serve Swagger UI for all APIs
docker run -d -p 8080:8080 \
  -v $(pwd)/libs/contracts:/usr/share/nginx/html/specs \
  -e URLS="[{url: '/specs/auth.yaml', name: 'Auth API'}, {url: '/specs/profile.yaml', name: 'Profile API'}, {url: '/specs/content.yaml', name: 'Content API'}, {url: '/specs/notifications.yaml', name: 'Notifications API'}, {url: '/specs/chat.yaml', name: 'Chat API'}, {url: '/specs/analytics.yaml', name: 'Analytics API'}]" \
  swaggerapi/swagger-ui

# Access at: http://45.146.164.70:8080
```

### 4.3. Infrastructure Service Endpoints

| Service | Endpoint | Credentials |
|---------|----------|-------------|
| **MinIO Console** | http://minio.45.146.164.70.nip.io | admin / admin123456 |
| **MinIO API** | http://minio-api.45.146.164.70.nip.io | admin / admin123456 |
| **Grafana** | http://grafana.45.146.164.70.nip.io | admin / admin123 |
| **Prometheus** | http://prometheus.45.146.164.70.nip.io | No auth |
| **RabbitMQ Management** | http://rabbitmq.45.146.164.70.nip.io | admin / admin123 |

### 4.4. Health Check Endpoints

All services expose health check endpoints:
- **Health**: `GET /healthz` - Basic health check
- **Readiness**: `GET /readyz` - Readiness probe
- **Metrics**: `GET /metrics` - Prometheus metrics

## 5. Environment Variables Management

### 5.1. Environment Structure

The project supports three environments:
- **dev**: Development environment (auto-deployed from `dev` branch)
- **staging**: Staging environment (manual deployment)
- **prod**: Production environment (deployed from release tags)

### 5.2. Configuration Files Locations

#### Helm Values Files:
```
deploy/helm/{service}/values.yaml          # Base configuration
deploy/helm/{service}/values.dev.yaml      # Dev environment overrides
deploy/helm/{service}/values.staging.yaml  # Staging environment overrides (create if needed)
deploy/helm/{service}/values.prod.yaml     # Production environment overrides (create if needed)
```

#### Kubernetes Secrets and ConfigMaps:
```bash
# View current environment variables for a service
kubectl get deployment auth -n dev -o yaml | grep -A 20 env:

# Update environment variables via Helm
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  --set env[0].name=DATABASE_URL \
  --set env[0].value="postgresql://user:pass@postgresql.postgresql.svc.cluster.local:5432/aiproject"
```

### 5.3. Common Environment Variables

#### Database Configuration:
```yaml
env:
  - name: DATABASE_URL
    value: "postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject"
  - name: REDIS_URL
    value: "redis://redis-master.redis.svc.cluster.local:6379"
  - name: RABBITMQ_URL
    value: "amqp://admin:admin123@rabbitmq.rabbitmq.svc.cluster.local:5672"
```

#### MinIO Configuration:
```yaml
env:
  - name: MINIO_ENDPOINT
    value: "minio.minio.svc.cluster.local:9000"
  - name: MINIO_ACCESS_KEY
    value: "admin"
  - name: MINIO_SECRET_KEY
    value: "admin123456"
  - name: MINIO_SECURE
    value: "false"
```

#### Service-Specific Variables:
```yaml
# Auth Service
env:
  - name: JWT_SECRET
    value: "your-jwt-secret-key"
  - name: JWT_ALGORITHM
    value: "HS256"
  - name: ACCESS_TOKEN_EXPIRE_MINUTES
    value: "60"
  - name: REFRESH_TOKEN_EXPIRE_DAYS
    value: "30"

# Notifications Service
env:
  - name: SMTP_HOST
    value: "smtp.gmail.com"
  - name: SMTP_PORT
    value: "587"
  - name: SMTP_USER
    value: "your-email@gmail.com"
  - name: SMTP_PASSWORD
    value: "your-app-password"
  - name: TELEGRAM_BOT_TOKEN
    value: "your-telegram-bot-token"
```

### 5.4. How to Update Environment Variables

#### Method 1: Update Helm Values Files
```bash
# Edit the values file for specific environment
vim deploy/helm/auth/values.dev.yaml

# Add or modify environment variables
env:
  - name: NEW_VARIABLE
    value: "new-value"

# Redeploy the service
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  -f deploy/helm/auth/values.dev.yaml
```

#### Method 2: Use Kubernetes Secrets
```bash
# Create a secret for sensitive data
kubectl create secret generic auth-secrets \
  --namespace=dev \
  --from-literal=jwt-secret=your-super-secret-key \
  --from-literal=database-password=secure-password

# Reference in deployment via values file:
env:
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: auth-secrets
        key: jwt-secret
```

#### Method 3: Direct Helm Set
```bash
# Update single environment variable
helm upgrade auth deploy/helm/auth \
  --namespace dev \
  --set env[0].name=LOG_LEVEL \
  --set env[0].value=DEBUG \
  --reuse-values
```

## 6. CI/CD Pipeline Configuration

### 6.1. GitHub Secrets Setup

Add these secrets to your GitHub repository:

#### Repository Secrets:
- `GHCR_USERNAME`: Your GitHub username (M1aso)
- `GHCR_TOKEN`: GitHub Personal Access Token with packages:write permission

#### Environment Secrets (for each environment):

**Dev Environment:**
- `KUBE_CONFIG`: Base64 encoded kubeconfig file for VPS access

```bash
# Generate kubeconfig for GitHub Actions
# On your VPS, run:
sudo cat /etc/rancher/k3s/k3s.yaml | sed 's/127.0.0.1/45.146.164.70/g' | base64 -w 0

# Add this output as KUBE_CONFIG secret in GitHub repository settings
# under Settings > Environments > dev > Environment secrets
```

### 6.2. Workflow Triggers

- **Dev Branch**: Automatic deployment to dev environment on push
- **Main Branch**: Build and push images only
- **Release Tags**: Automatic deployment to production
- **Manual**: Deploy any environment via workflow_dispatch

### 6.3. Creating a Release

```bash
# Create and push a release tag
git tag release-1.0.0
git push origin release-1.0.0

# This will automatically deploy to production
```

## 7. Monitoring and Logs

### 7.1. Grafana Dashboards

Access Grafana at http://grafana.45.146.164.70.nip.io (admin/admin123)

**Pre-configured Dashboards:**
- Kubernetes Cluster Overview
- Node Exporter Full
- Kubernetes Pods
- NGINX Ingress Controller

**Custom Dashboards to Import:**
- Dashboard ID 3119: Kubernetes cluster monitoring
- Dashboard ID 7249: Kubernetes cluster monitoring (Prometheus)

### 7.2. Application Metrics

All services expose Prometheus metrics at `/metrics` endpoint:
- Request counters
- Response time histograms
- Error rates
- Custom business metrics

### 7.3. Log Aggregation

```bash
# View logs for specific service
kubectl logs -f deployment/auth -n dev

# View logs for all pods in namespace
kubectl logs -f -l app=auth -n dev

# Stream logs from multiple services
kubectl logs -f -l "app in (auth,profile,content)" -n dev
```

## 8. Backup and Maintenance

### 8.1. Database Backups

```bash
# Create backup script
cat <<EOF > /opt/backup-db.sh
#!/bin/bash
DATE=\$(date +%Y%m%d_%H%M%S)
kubectl exec -n postgresql postgresql-0 -- pg_dump -U postgres aiproject > /opt/backups/db_backup_\$DATE.sql
find /opt/backups -name "db_backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/backup-db.sh

# Setup cron job for daily backups
echo "0 2 * * * /opt/backup-db.sh" | crontab -
```

### 8.2. MinIO Data Backup

```bash
# Backup MinIO data
rsync -av /opt/minio-data/ /opt/backups/minio_$(date +%Y%m%d)/
```

## 9. Troubleshooting

### 9.1. Common Issues

#### Service Not Starting:
```bash
# Check pod status
kubectl get pods -n dev

# Check pod logs
kubectl logs deployment/auth -n dev

# Describe pod for events
kubectl describe pod <pod-name> -n dev
```

#### Database Connection Issues:
```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql postgresql://postgres:postgres123@postgresql.postgresql.svc.cluster.local:5432/aiproject
```

#### Image Pull Issues:
```bash
# Check if GHCR secret exists
kubectl get secret ghcr -n dev

# Recreate GHCR secret if needed
kubectl delete secret ghcr -n dev
kubectl create secret docker-registry ghcr \
  --docker-server=ghcr.io \
  --docker-username=M1aso \
  --docker-password=<YOUR_GITHUB_TOKEN> \
  --namespace=dev
```

### 9.2. Service Discovery

```bash
# List all services in dev namespace
kubectl get svc -n dev

# Check ingress status
kubectl get ingress -A

# Test internal service communication
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://auth.dev.svc.cluster.local:8000/healthz
```

## 10. Security Considerations

### 10.1. TLS/SSL Setup

For production, configure TLS certificates:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 10.2. Network Policies

```bash
# Apply network policies for isolation
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: dev
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
EOF
```

## 11. Development Workflow

### 11.1. Local Development

```bash
# Clone repository
git clone https://github.com/M1aso/ai-project.git
cd ai-project

# Create feature branch
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name

# Create PR to dev branch
# After merge, changes will auto-deploy to dev environment
```

### 11.2. Promotion to Production

```bash
# Create release from main branch
git checkout main
git pull origin main
git tag release-1.0.0
git push origin release-1.0.0

# This triggers automatic production deployment
```

## 12. Quick Reference Commands

```bash
# Check all pods across environments
kubectl get pods -A

# Scale a service
kubectl scale deployment auth --replicas=3 -n dev

# Update a service image
kubectl set image deployment/auth auth=ghcr.io/m1aso/auth:new-tag -n dev

# Port forward for local access
kubectl port-forward svc/auth 8000:8000 -n dev

# Execute into a pod
kubectl exec -it deployment/auth -n dev -- /bin/bash

# View resource usage
kubectl top pods -n dev
kubectl top nodes
```