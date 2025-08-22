#!/bin/bash

# VPS Setup Script for AI Project
# Usage: ./setup-vps.sh [dev|staging|prod]

set -euo pipefail

ENVIRONMENT=${1:-dev}
VPS_IP="45.146.164.70"

echo "🚀 Setting up VPS for environment: $ENVIRONMENT"
echo "📍 VPS IP: $VPS_IP"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

# 1. System Update and Basic Tools
log_info "Updating system and installing basic tools..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl wget git vim htop unzip software-properties-common \
    apt-transport-https ca-certificates gnupg lsb-release jq

# 2. Install Docker
log_info "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
    log_info "Docker installed successfully"
else
    log_info "Docker already installed"
fi

# 3. Install k3s
log_info "Installing k3s..."
if ! command -v kubectl &> /dev/null; then
    # Install k3s with proper kubeconfig permissions
    curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
    
    # Wait for k3s to be ready
    log_info "Waiting for k3s to be ready..."
    sleep 10
    sudo systemctl enable k3s
    sudo systemctl start k3s
    
    # Wait for kubeconfig file to be created
    timeout=60
    while [ ! -f /etc/rancher/k3s/k3s.yaml ] && [ $timeout -gt 0 ]; do
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [ ! -f /etc/rancher/k3s/k3s.yaml ]; then
        log_error "k3s kubeconfig file not created after waiting"
        exit 1
    fi
    
    # Set up kubectl configuration
    mkdir -p ~/.kube
    sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
    sudo chown $USER:$USER ~/.kube/config
    
    # Add kubectl to PATH (k3s installs it as k3s kubectl)
    sudo ln -sf /usr/local/bin/k3s /usr/local/bin/kubectl
    
    # Set environment variable
    echo "export KUBECONFIG=~/.kube/config" >> ~/.bashrc
    export KUBECONFIG=~/.kube/config
    
    # Wait for k3s to be fully operational
    log_info "Waiting for k3s cluster to be ready..."
    kubectl wait --for=condition=Ready nodes --all --timeout=120s
    
    log_info "k3s installed successfully"
else
    log_info "kubectl already available"
    # Ensure kubeconfig is properly set even if kubectl exists
    if [ -f /etc/rancher/k3s/k3s.yaml ]; then
        mkdir -p ~/.kube
        sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
        sudo chown $USER:$USER ~/.kube/config
        export KUBECONFIG=~/.kube/config
    fi
fi

# 4. Install Helm
log_info "Installing Helm..."
if ! command -v helm &> /dev/null; then
    curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
    sudo apt update
    sudo apt install -y helm
    log_info "Helm installed successfully"
else
    log_info "Helm already installed"
fi

# 5. Install NGINX Ingress Controller
log_info "Installing NGINX Ingress Controller..."

# Verify kubectl is working before proceeding
if ! kubectl cluster-info &> /dev/null; then
    log_error "kubectl is not properly configured. Please check k3s installation."
    log_info "Trying to fix kubeconfig permissions..."
    
    if [ -f /etc/rancher/k3s/k3s.yaml ]; then
        sudo chmod 644 /etc/rancher/k3s/k3s.yaml
        mkdir -p ~/.kube
        sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
        sudo chown $USER:$USER ~/.kube/config
        export KUBECONFIG=~/.kube/config
        
        # Test again
        if ! kubectl cluster-info &> /dev/null; then
            log_error "Still cannot access Kubernetes cluster. Exiting."
            exit 1
        fi
        log_info "Fixed kubeconfig permissions successfully"
    else
        log_error "k3s kubeconfig file not found. Please restart k3s installation."
        exit 1
    fi
fi

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

log_info "Waiting for NGINX Ingress Controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# 6. Add Helm repositories
log_info "Adding Helm repositories..."
# Note: Bitnami charts are now distributed via OCI registry, no need to add traditional repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 7. Install PostgreSQL
log_info "Installing PostgreSQL..."
if ! kubectl get namespace postgresql &> /dev/null; then
    helm install postgresql oci://registry-1.docker.io/bitnamicharts/postgresql \
      --namespace postgresql \
      --create-namespace \
      --set auth.postgresPassword=postgres123 \
      --set auth.database=aiproject \
      --set primary.persistence.size=10Gi \
      --wait
    log_info "PostgreSQL installed successfully"
else
    log_info "PostgreSQL already installed"
fi

# 8. Install Redis
log_info "Installing Redis..."
if ! kubectl get namespace redis &> /dev/null; then
    helm install redis oci://registry-1.docker.io/bitnamicharts/redis \
      --namespace redis \
      --create-namespace \
      --set auth.enabled=false \
      --set master.persistence.size=5Gi \
      --wait
    log_info "Redis installed successfully"
else
    log_info "Redis already installed"
fi

# 9. Install RabbitMQ
log_info "Installing RabbitMQ..."
if ! kubectl get namespace rabbitmq &> /dev/null; then
    helm install rabbitmq oci://registry-1.docker.io/bitnamicharts/rabbitmq \
      --namespace rabbitmq \
      --create-namespace \
      --set auth.username=admin \
      --set auth.password=admin123 \
      --set service.type=ClusterIP \
      --wait
    
    # Create RabbitMQ ingress
    cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rabbitmq-ingress
  namespace: rabbitmq
spec:
  ingressClassName: nginx
  rules:
  - host: rabbitmq.$VPS_IP.nip.io
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
    log_info "RabbitMQ installed successfully"
else
    log_info "RabbitMQ already installed"
fi

# 10. Install MinIO
log_info "Installing MinIO..."
if ! kubectl get namespace minio &> /dev/null; then
    kubectl create namespace minio
    sudo mkdir -p /opt/minio-data
    
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
  - host: minio.$VPS_IP.nip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: minio
            port:
              number: 9001
  - host: minio-api.$VPS_IP.nip.io
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
    log_info "MinIO installed successfully"
else
    log_info "MinIO already installed"
fi

# 11. Install Prometheus & Grafana
log_info "Installing Prometheus & Grafana..."
if ! kubectl get namespace monitoring &> /dev/null; then
    helm install monitoring prometheus-community/kube-prometheus-stack \
      --namespace monitoring \
      --create-namespace \
      --set grafana.adminPassword=admin123 \
      --set grafana.service.type=ClusterIP \
      --set prometheus.service.type=ClusterIP \
      --wait
    
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
  - host: grafana.$VPS_IP.nip.io
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
  - host: prometheus.$VPS_IP.nip.io
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
    log_info "Prometheus & Grafana installed successfully"
else
    log_info "Monitoring stack already installed"
fi

# 12. Create backup directories
log_info "Setting up backup directories..."
sudo mkdir -p /opt/backups
sudo chown $USER:$USER /opt/backups

# 13. Create backup script
log_info "Creating backup script..."
cat <<'EOF' > /opt/backup-db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p /opt/backups
kubectl exec -n postgresql postgresql-0 -- pg_dump -U postgres aiproject > /opt/backups/db_backup_$DATE.sql
find /opt/backups -name "db_backup_*.sql" -mtime +7 -delete
echo "Database backup completed: db_backup_$DATE.sql"
EOF

chmod +x /opt/backup-db.sh

# Setup cron job for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-db.sh") | crontab -

# 14. Display summary
log_info "🎉 VPS setup completed successfully!"
echo ""
echo "📋 Summary of installed services:"
echo "=================================="
echo "• Kubernetes (k3s): $(kubectl version --client --short)"
echo "• Helm: $(helm version --short)"
echo "• Docker: $(docker --version)"
echo ""
echo "🌐 Service Endpoints:"
echo "===================="
echo "• API Gateway: http://api.$VPS_IP.nip.io"
echo "• MinIO Console: http://minio.$VPS_IP.nip.io (admin/admin123456)"
echo "• MinIO API: http://minio-api.$VPS_IP.nip.io"
echo "• Grafana: http://grafana.$VPS_IP.nip.io (admin/admin123)"
echo "• Prometheus: http://prometheus.$VPS_IP.nip.io"
echo "• RabbitMQ: http://rabbitmq.$VPS_IP.nip.io (admin/admin123)"
echo ""
echo "📚 Next Steps:"
echo "=============="
echo "1. Clone your repository: git clone https://github.com/M1aso/ai-project.git"
echo "2. Create GitHub secrets for CI/CD (see DEPLOYMENT.md)"
echo "3. Push to dev branch to trigger automatic deployment"
echo "4. Access API documentation at: http://docs.$VPS_IP.nip.io (after app deployment)"
echo ""
echo "🔧 Useful Commands:"
echo "=================="
echo "• Check all pods: kubectl get pods -A"
echo "• View logs: kubectl logs -f deployment/auth -n dev"
echo "• Scale service: kubectl scale deployment auth --replicas=3 -n dev"
echo ""
echo "📖 Full documentation available in DEPLOYMENT.md"