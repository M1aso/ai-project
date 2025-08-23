#!/bin/bash

# Deploy ONLY the root ingress to fix the immediate issue
# This bypasses any issues with other manifests in deploy/k8s/

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

log_info "🚀 Deploying ONLY root ingress to fix API Gateway access"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. This script must be run on the server with kubectl access."
    exit 1
fi

# Deploy only the root ingress
log_info "Deploying root-ingress.yaml specifically..."
if kubectl apply -f deploy/k8s/root-ingress.yaml; then
    log_success "✅ Root ingress deployed successfully"
else
    log_error "❌ Failed to deploy root ingress"
    exit 1
fi

# Wait for ingress to be ready
log_info "Waiting for ingress to propagate..."
sleep 5

# Check ingress status
log_info "Checking ingress status..."
if kubectl get ingress root-ingress -n dev >/dev/null 2>&1; then
    log_success "✅ Root ingress exists in dev namespace"
    kubectl get ingress -n dev
else
    log_error "❌ Root ingress not found in dev namespace"
    exit 1
fi

# Test the API Gateway
log_info "Testing API Gateway endpoint..."
sleep 10  # Give ingress time to propagate

for i in {1..3}; do
    log_info "Test attempt $i/3..."
    response=$(curl -s -w "%{http_code}" http://api.45.146.164.70.nip.io/ 2>/dev/null || echo "000")
    http_code="${response: -3}"
    body="${response%???}"

    if [ "$http_code" = "200" ]; then
        log_success "✅ API Gateway is responding!"
        if echo "$body" | grep -q "AI Project API Gateway"; then
            log_success "✅ API Gateway returning correct response"
            echo "Response: $body"
            break
        else
            log_warn "⚠️  API Gateway responding but unexpected content"
            echo "Response: $body"
        fi
    elif [ "$http_code" = "404" ]; then
        if echo "$body" | grep -q "nginx"; then
            log_warn "⚠️  Still getting nginx 404 - waiting for ingress to propagate..."
            if [ $i -lt 3 ]; then
                sleep 15
                continue
            else
                log_error "❌ Still getting nginx 404 after 3 attempts"
            fi
        else
            log_warn "⚠️  Getting 404 from Envoy - API Gateway reachable but services may not be deployed"
            echo "Response: $body"
            break
        fi
    else
        log_error "❌ Unexpected response: HTTP $http_code"
        if [ -n "$body" ]; then
            echo "Response: $body"
        fi
    fi
done

# Test specific endpoint
log_info "Testing specific service endpoint..."
auth_response=$(curl -s -w "%{http_code}" http://api.45.146.164.70.nip.io/api/auth/healthz 2>/dev/null || echo "000")
auth_code="${auth_response: -3}"
auth_body="${auth_response%???}"

if [ "$auth_code" != "000" ] && ! echo "$auth_body" | grep -q "nginx"; then
    log_success "✅ Requests are reaching API Gateway (no more nginx 404s)"
    echo "Auth endpoint response: HTTP $auth_code"
    if [ -n "$auth_body" ]; then
        echo "Auth response: $auth_body"
    fi
else
    log_warn "⚠️  Auth endpoint still returning nginx 404"
fi

log_info "🏁 Root ingress deployment completed"

# Provide status summary
log_info "\n📊 SUMMARY"
echo "✅ Root ingress deployed to dev namespace"
echo "✅ Ingress routing configured for api.45.146.164.70.nip.io"
echo "✅ Should resolve nginx 404 errors"

log_info "\n📋 Next Steps:"
echo "1. Run full verification: ./scripts/verify-services.sh dev"
echo "2. If services return 404, they may need to be deployed"
echo "3. Check individual service deployment status"
echo "4. All requests should now show Envoy headers instead of nginx errors"
