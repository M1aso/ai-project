#!/bin/bash

# Service verification script for AI Project
# This script checks if all services are properly deployed and accessible

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

# Configuration
ENVIRONMENT=${1:-dev}
BASE_URL="http://api.45.146.164.70.nip.io"
SERVICES=("auth" "profile" "content" "notifications" "analytics")

log_info "🔍 Verifying AI Project services in $ENVIRONMENT environment"
log_info "Base URL: $BASE_URL"

# Test API Gateway root
log_info "\n📡 Testing API Gateway..."
if response=$(curl -s "$BASE_URL/" 2>/dev/null); then
    if echo "$response" | grep -q "AI Project API Gateway"; then
        log_success "✅ API Gateway is responding"
    else
        log_warn "⚠️  API Gateway responding but with unexpected content"
        echo "Response: $response"
    fi
else
    log_error "❌ API Gateway not responding"
fi

# Test each service health endpoint
log_info "\n🏥 Testing service health endpoints..."
for service in "${SERVICES[@]}"; do
    log_info "Testing $service..."
    
    # Test health endpoint
    health_url="$BASE_URL/api/$service/healthz"
    if response=$(curl -s -w "%{http_code}" "$health_url" 2>/dev/null); then
        http_code="${response: -3}"
        body="${response%???}"
        
        if [ "$http_code" = "200" ]; then
            log_success "✅ $service health check OK"
            if echo "$body" | grep -q "\"service\":\"$service\""; then
                log_success "   Service identity confirmed"
            else
                log_warn "   Service responding but identity unclear: $body"
            fi
        else
            log_error "❌ $service health check failed (HTTP $http_code)"
            if [ -n "$body" ]; then
                echo "   Response: $body"
            fi
        fi
    else
        log_error "❌ $service health check failed (no response)"
    fi
done

# Test specific service endpoints
log_info "\n🧪 Testing specific service endpoints..."

# Test content service courses endpoint
log_info "Testing content service courses..."
courses_url="$BASE_URL/api/content/courses"
if response=$(curl -s -w "%{http_code}" "$courses_url" 2>/dev/null); then
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        log_success "✅ Content courses endpoint OK"
        echo "   Response: $body"
    else
        log_error "❌ Content courses endpoint failed (HTTP $http_code)"
        if [ -n "$body" ]; then
            echo "   Response: $body"
        fi
    fi
else
    log_error "❌ Content courses endpoint failed (no response)"
fi

# Test auth service endpoints (non-authenticated)
log_info "Testing auth service endpoints..."
login_url="$BASE_URL/api/auth/login"
if response=$(curl -s -w "%{http_code}" -X POST "$login_url" \
    -H "Content-Type: application/json" \
    -d '{"email": "test@example.com", "password": "test123"}' 2>/dev/null); then
    http_code="${response: -3}"
    body="${response%???}"
    
    # We expect 400/401/422 for invalid credentials, not 404
    if [ "$http_code" != "404" ] && [ "$http_code" != "000" ]; then
        log_success "✅ Auth login endpoint responding (HTTP $http_code)"
        echo "   Response: $body"
    else
        log_error "❌ Auth login endpoint not found (HTTP $http_code)"
        if [ -n "$body" ]; then
            echo "   Response: $body"
        fi
    fi
else
    log_error "❌ Auth login endpoint failed (no response)"
fi

# Summary
log_info "\n📊 Summary"
echo "If you see 404 errors, the services might not be deployed or the API gateway routing is incorrect."
echo "If you see connection errors, check if the API gateway is running."
echo ""
echo "To deploy services, run:"
echo "  ./scripts/manage-env.sh deploy $ENVIRONMENT <service-name>"
echo ""
echo "To check Kubernetes status (if kubectl is available):"
echo "  kubectl get pods -n $ENVIRONMENT"
echo "  kubectl get services -n $ENVIRONMENT"
echo "  kubectl get ingress -n $ENVIRONMENT"

log_info "🏁 Service verification completed"
