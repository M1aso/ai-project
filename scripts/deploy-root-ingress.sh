#!/bin/bash

# Manual deployment script for root ingress
# This deploys the root ingress that was missing from the GitHub Actions workflow

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

ENVIRONMENT=${1:-dev}

log_info "🚀 Deploying root ingress to $ENVIRONMENT environment"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. Please install kubectl or run this on the server."
    exit 1
fi

# Deploy the root ingress
log_info "Deploying deploy/k8s/root-ingress.yaml..."
if kubectl apply -f deploy/k8s/root-ingress.yaml; then
    log_success "✅ Root ingress deployed successfully"
else
    log_error "❌ Failed to deploy root ingress"
    exit 1
fi

# Wait a moment for ingress to be ready
log_info "Waiting for ingress to be ready..."
sleep 5

# Check ingress status
log_info "Checking ingress status..."
kubectl get ingress root-ingress -n "$ENVIRONMENT" || log_warn "Root ingress not found in $ENVIRONMENT namespace"

# Test the endpoint
log_info "Testing API Gateway endpoint..."
sleep 3  # Give ingress a moment to propagate

response=$(curl -s -w "%{http_code}" http://api.45.146.164.70.nip.io/ 2>/dev/null || echo "000")
http_code="${response: -3}"
body="${response%???}"

if [ "$http_code" = "200" ]; then
    log_success "✅ API Gateway is responding!"
    if echo "$body" | grep -q "AI Project API Gateway"; then
        log_success "✅ API Gateway returning correct response"
        echo "Response: $body"
    else
        log_warn "⚠️  API Gateway responding but unexpected content"
        echo "Response: $body"
    fi
elif [ "$http_code" = "404" ]; then
    if echo "$body" | grep -q "nginx"; then
        log_error "❌ Still getting nginx 404 - ingress may not be routing properly"
    else
        log_warn "⚠️  Getting 404 but from Envoy - check if services are deployed"
    fi
else
    log_error "❌ Unexpected response: HTTP $http_code"
    if [ -n "$body" ]; then
        echo "Response: $body"
    fi
fi

log_info "🏁 Root ingress deployment completed"

# Provide next steps
log_info "\n📋 Next Steps:"
echo "1. Test all endpoints: ./scripts/verify-services.sh $ENVIRONMENT"
echo "2. If still getting 404s, check if individual services are deployed"
echo "3. Check ingress status: kubectl describe ingress root-ingress -n $ENVIRONMENT"
echo "4. Check API Gateway logs: kubectl logs deployment/api-gateway -n $ENVIRONMENT"
