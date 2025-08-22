#!/bin/bash

# K3s Troubleshooting and Fix Script
# Usage: ./fix-k3s.sh

set -euo pipefail

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

log_info "🔧 K3s Troubleshooting Script"
echo "============================="

# Check if k3s is installed
if ! command -v k3s &> /dev/null; then
    log_error "k3s is not installed. Please run the setup script first."
    exit 1
fi

# Check k3s service status
log_info "Checking k3s service status..."
if ! sudo systemctl is-active --quiet k3s; then
    log_warn "k3s service is not running. Starting it..."
    sudo systemctl start k3s
    sleep 5
fi

# Enable k3s service if not enabled
if ! sudo systemctl is-enabled --quiet k3s; then
    log_info "Enabling k3s service..."
    sudo systemctl enable k3s
fi

# Wait for k3s to create the kubeconfig file
log_info "Waiting for k3s kubeconfig file..."
timeout=60
while [ ! -f /etc/rancher/k3s/k3s.yaml ] && [ $timeout -gt 0 ]; do
    sleep 2
    timeout=$((timeout-2))
    echo -n "."
done
echo ""

if [ ! -f /etc/rancher/k3s/k3s.yaml ]; then
    log_error "k3s kubeconfig file not found after waiting. Restarting k3s..."
    sudo systemctl restart k3s
    sleep 10
    
    # Check again
    if [ ! -f /etc/rancher/k3s/k3s.yaml ]; then
        log_error "k3s kubeconfig file still not found. There might be an installation issue."
        log_info "Checking k3s logs:"
        sudo journalctl -u k3s --no-pager -l -n 20
        exit 1
    fi
fi

# Fix kubeconfig permissions
log_info "Fixing kubeconfig permissions..."
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# Set up user kubeconfig
log_info "Setting up user kubeconfig..."
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

# Ensure kubectl is available
if [ ! -f /usr/local/bin/kubectl ]; then
    log_info "Creating kubectl symlink..."
    sudo ln -sf /usr/local/bin/k3s /usr/local/bin/kubectl
fi

# Set environment variable
export KUBECONFIG=~/.kube/config

# Test kubectl
log_info "Testing kubectl access..."
if kubectl cluster-info &> /dev/null; then
    log_info "✅ kubectl is working correctly!"
    
    # Show cluster status
    echo ""
    log_info "Cluster Status:"
    kubectl get nodes
    echo ""
    kubectl get pods -A | head -10
    
else
    log_error "❌ kubectl is still not working. Here's some debug info:"
    echo ""
    echo "k3s service status:"
    sudo systemctl status k3s --no-pager -l
    echo ""
    echo "kubeconfig file permissions:"
    ls -la /etc/rancher/k3s/k3s.yaml
    echo ""
    echo "User kubeconfig permissions:"
    ls -la ~/.kube/config 2>/dev/null || echo "User kubeconfig not found"
    exit 1
fi

log_info "🎉 K3s is now properly configured!"
echo ""
echo "You can now continue with the setup script or run kubectl commands directly."
echo "Environment variable set: KUBECONFIG=~/.kube/config"
echo ""
echo "To make this permanent, add this to your ~/.bashrc:"
echo "export KUBECONFIG=~/.kube/config"