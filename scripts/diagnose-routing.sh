#!/bin/bash

# Comprehensive routing diagnostic script
# This script tests various routing scenarios to identify the exact issue

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
BASE_URL="http://api.45.146.164.70.nip.io"

log_info "🔍 Comprehensive Routing Diagnostics"
log_info "Base URL: $BASE_URL"

# Test different paths to understand routing behavior
test_path() {
    local path="$1"
    local description="$2"
    
    log_info "\n🧪 Testing: $description"
    log_info "URL: $BASE_URL$path"
    
    # Get full response with headers
    response=$(curl -v -s "$BASE_URL$path" 2>&1)
    
    # Extract HTTP status
    http_status=$(echo "$response" | grep "< HTTP" | tail -1 || echo "No HTTP status found")
    
    # Check for Envoy headers (indicates request reached API gateway)
    envoy_header=$(echo "$response" | grep -i "x-envoy" || echo "")
    
    # Extract response body
    body=$(echo "$response" | sed -n '/^$/,$p' | tail -n +2)
    
    echo "HTTP Status: $http_status"
    if [ -n "$envoy_header" ]; then
        log_success "✅ Request reached Envoy (API Gateway)"
        echo "Envoy header: $envoy_header"
    else
        log_error "❌ Request did NOT reach Envoy (bypassed API Gateway)"
    fi
    
    if [ -n "$body" ]; then
        echo "Response body: $body"
    else
        echo "Response body: (empty)"
    fi
    
    # Analyze response type
    if echo "$body" | grep -q "nginx"; then
        log_warn "⚠️  Response from nginx (not API gateway)"
    elif echo "$body" | grep -q '"detail"'; then
        log_warn "⚠️  FastAPI error response"
    elif echo "$body" | grep -q "404 page not found"; then
        log_warn "⚠️  Go service error response"
    elif echo "$body" | grep -q '"status"'; then
        log_success "✅ Structured API response"
    fi
}

# Test various routing scenarios
log_info "🚀 Starting routing diagnostics...\n"

# Test root path (should hit catch-all route)
test_path "/" "Root path (/) - should return API gateway info"

# Test /api path (should hit catch-all route)  
test_path "/api" "API base path (/api) - should return API gateway info"

# Test specific service paths
test_path "/api/auth" "Auth service base (/api/auth)"
test_path "/api/auth/healthz" "Auth health check (/api/auth/healthz)"
test_path "/api/content" "Content service base (/api/content)"
test_path "/api/content/healthz" "Content health check (/api/content/healthz)"
test_path "/api/content/courses" "Content courses (/api/content/courses)"

# Test non-existent paths
test_path "/nonexistent" "Non-existent path - should hit catch-all"
test_path "/api/nonexistent" "Non-existent API path - should hit catch-all"

# Test with different methods
log_info "\n🔧 Testing POST request to auth..."
post_response=$(curl -v -s -X POST "$BASE_URL/api/auth/phone/send-code" \
    -H "Content-Type: application/json" \
    -d '{"phone": "+79001234567"}' 2>&1)

post_status=$(echo "$post_response" | grep "< HTTP" | tail -1 || echo "No HTTP status")
post_envoy=$(echo "$post_response" | grep -i "x-envoy" || echo "")
post_body=$(echo "$post_response" | sed -n '/^$/,$p' | tail -n +2)

echo "POST Status: $post_status"
if [ -n "$post_envoy" ]; then
    log_success "✅ POST reached Envoy"
else
    log_error "❌ POST did NOT reach Envoy"
fi
echo "POST Body: $post_body"

# Summary and recommendations
log_info "\n📊 DIAGNOSTIC SUMMARY"
echo "=============================="

log_info "🔍 Analysis:"
echo "1. If NO requests show Envoy headers → API Gateway not receiving traffic"
echo "2. If SOME requests show Envoy headers → Partial routing working"
echo "3. If ALL requests show Envoy headers but return errors → Backend services down"

log_info "\n🛠️  Potential Issues:"
echo "- Ingress configuration conflicts"
echo "- API Gateway service not deployed/running"
echo "- Backend services not deployed/accessible"
echo "- Envoy configuration errors"
echo "- DNS/networking issues"

log_info "\n🚀 Recommended Actions:"
echo "1. If no Envoy headers: Check ingress configuration and API gateway deployment"
echo "2. If Envoy headers present: Check backend service deployment and Envoy clusters"
echo "3. Check Kubernetes resources: pods, services, ingresses"

log_info "\n🏁 Diagnostic completed"
