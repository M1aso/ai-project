#!/bin/bash

# Deploy monitoring ingress resources
# This script applies the monitoring ingress configurations to fix 404 errors

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "🚀 Deploying monitoring ingress resources"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. Please install kubectl or run this on the server."
    exit 1
fi

# Check if we can connect to the cluster
if ! kubectl cluster-info &> /dev/null; then
    log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Apply monitoring ingress
log_info "Applying monitoring ingress configurations..."
if kubectl apply -f deploy/k8s/monitoring-ingress.yaml; then
    log_success "✅ Monitoring ingress applied successfully"
else
    log_error "❌ Failed to apply monitoring ingress"
    exit 1
fi

# Wait for ingress to be ready
log_info "Waiting for ingress resources to be ready..."
sleep 10

# Check ingress status
log_info "Checking ingress status..."
kubectl get ingress -n monitoring
kubectl get ingress -n rabbitmq

# Test the endpoints
log_info "Testing monitoring endpoints..."
sleep 5  # Give ingress a moment to propagate

# Test Grafana
log_info "Testing Grafana endpoint..."
response=$(curl -s -w "%{http_code}" http://grafana.45.146.164.70.nip.io/ 2>/dev/null || echo "000")
http_code="${response: -3}"
if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
    log_success "✅ Grafana is responding!"
elif [ "$http_code" = "404" ]; then
    log_error "❌ Grafana still returning 404"
else
    log_warn "⚠️  Grafana returned HTTP $http_code"
fi

# Test Prometheus
log_info "Testing Prometheus endpoint..."
response=$(curl -s -w "%{http_code}" http://prometheus.45.146.164.70.nip.io/ 2>/dev/null || echo "000")
http_code="${response: -3}"
if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
    log_success "✅ Prometheus is responding!"
elif [ "$http_code" = "404" ]; then
    log_error "❌ Prometheus still returning 404"
else
    log_warn "⚠️  Prometheus returned HTTP $http_code"
fi

# Test RabbitMQ
log_info "Testing RabbitMQ endpoint..."
response=$(curl -s -w "%{http_code}" http://rabbitmq.45.146.164.70.nip.io/ 2>/dev/null || echo "000")
http_code="${response: -3}"
if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
    log_success "✅ RabbitMQ is responding!"
elif [ "$http_code" = "404" ]; then
    log_error "❌ RabbitMQ still returning 404"
else
    log_warn "⚠️  RabbitMQ returned HTTP $http_code"
fi

log_info "🏁 Monitoring ingress deployment completed"

# Provide troubleshooting steps
log_info "\n🔍 Troubleshooting:"
echo "1. Check service names: kubectl get svc -n monitoring && kubectl get svc -n rabbitmq"
echo "2. Check ingress details: kubectl describe ingress -n monitoring && kubectl describe ingress -n rabbitmq"
echo "3. Check pod status: kubectl get pods -n monitoring && kubectl get pods -n rabbitmq"
echo "4. View ingress controller logs: kubectl logs -n ingress-nginx deployment/ingress-nginx-controller"
