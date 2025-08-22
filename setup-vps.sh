#!/bin/bash

# VPS Setup Script for Dev Environment
# Run this ONCE on your VPS: ssh root@45.146.164.70

set -e

echo "🚀 Setting up VPS for AI Project Dev Environment"
echo "==============================================="

VPS_IP="45.146.164.70"

# Update system
echo "📦 Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y && apt-get upgrade -y

# Install required packages
echo "📦 Installing required packages..."
apt-get install -y curl git jq ca-certificates ufw docker.io

# Configure firewall
echo "🔒 Configuring firewall..."
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 6443/tcp # Kubernetes API
yes | ufw enable

# Start Docker
echo "🐳 Starting Docker..."
systemctl start docker
systemctl enable docker

# Install K3s if not already installed
if ! command -v k3s &> /dev/null; then
    echo "⚙️  Installing K3s..."
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable=traefik" sh -
else
    echo "✅ K3s already installed"
fi

# Install Helm if not already installed
if ! command -v helm &> /dev/null; then
    echo "⚙️  Installing Helm..."
    curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
else
    echo "✅ Helm already installed"
fi

# Set up kubectl config
echo "⚙️  Setting up kubectl..."
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Wait for K3s to be ready
echo "⏳ Waiting for K3s to be ready..."
sleep 30
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Install nginx ingress controller
echo "🌐 Installing nginx ingress controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

kubectl create namespace ingress-nginx --dry-run=client -o yaml | kubectl apply -f -

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --set controller.service.type=LoadBalancer \
  --set controller.watchIngressWithoutClass=true \
  --set controller.admissionWebhooks.enabled=true \
  --wait --timeout=300s

# Wait for ingress to get external IP
echo "⏳ Waiting for ingress to get external IP..."
kubectl -n ingress-nginx wait --for=condition=ready pod -l app.kubernetes.io/component=controller --timeout=300s

# Show ingress status
echo "📊 Ingress Controller Status:"
kubectl -n ingress-nginx get svc

# Create dev namespace
echo "📦 Creating dev namespace..."
kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -

echo
echo "🎉 VPS Setup Complete!"
echo "📍 Your dev environment is ready at: http://$VPS_IP.nip.io"
echo
echo "📋 Next steps:"
echo "1. Set up GitHub Actions secrets (run setup-vps-access.sh for instructions)"
echo "2. Push code to trigger deployment"
echo "3. Monitor deployment: kubectl -n dev get pods"
echo
echo "🔑 Kubeconfig for GitHub Actions:"
echo "Run this command and add the output as KUBE_CONFIG secret:"
echo "cat /etc/rancher/k3s/k3s.yaml | base64 -w 0"