#!/bin/bash

# Run tests for all services
# This script runs unit tests for each service

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Test results tracking
declare -A test_results

# Run Python service tests
test_python_service() {
    local service_name=$1
    
    log_step "Testing $service_name service..."
    
    cd "services/$service_name"
    
    if [ -d "venv" ] && [ -d "tests" ]; then
        source venv/bin/activate
        
        # Set test environment variables
        export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject_test"
        export REDIS_URL="redis://localhost:6379/1"  # Use different Redis DB for tests
        export LOG_LEVEL="WARNING"  # Reduce log noise during tests
        
        if python -m pytest tests/ -v --tb=short; then
            test_results[$service_name]="✅ PASSED"
            log_info "$service_name tests passed ✓"
        else
            test_results[$service_name]="❌ FAILED"
            log_error "$service_name tests failed ✗"
        fi
    else
        test_results[$service_name]="⚠️ SKIPPED"
        log_warn "$service_name: Tests skipped (no venv or tests directory)"
    fi
    
    cd ../..
}

# Test Go service
test_go_service() {
    log_step "Testing content service..."
    
    cd services/content
    
    export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject_test"
    export LOG_LEVEL="WARNING"
    
    if go test ./... -v; then
        test_results["content"]="✅ PASSED"
        log_info "Content service tests passed ✓"
    else
        test_results["content"]="❌ FAILED"
        log_error "Content service tests failed ✗"
    fi
    
    cd ../..
}

# Test Node.js service
test_node_service() {
    log_step "Testing chat service..."
    
    cd services/chat
    
    export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject_test"
    export REDIS_URL="redis://localhost:6379/1"
    export LOG_LEVEL="WARNING"
    
    if npm test; then
        test_results["chat"]="✅ PASSED"
        log_info "Chat service tests passed ✓"
    else
        test_results["chat"]="❌ FAILED"
        log_error "Chat service tests failed ✗"
    fi
    
    cd ../..
}

# Create test database
setup_test_database() {
    log_step "Setting up test database..."
    
    # Create test database
    docker exec ai-project-postgres psql -U postgres -c "DROP DATABASE IF EXISTS aiproject_test;" || true
    docker exec ai-project-postgres psql -U postgres -c "CREATE DATABASE aiproject_test;"
    
    log_info "Test database created ✓"
}

# Display test results summary
show_results() {
    echo
    echo "📊 Test Results Summary"
    echo "======================"
    
    local total=0
    local passed=0
    local failed=0
    local skipped=0
    
    for service in "${!test_results[@]}"; do
        echo "$service: ${test_results[$service]}"
        total=$((total + 1))
        
        if [[ "${test_results[$service]}" == *"PASSED"* ]]; then
            passed=$((passed + 1))
        elif [[ "${test_results[$service]}" == *"FAILED"* ]]; then
            failed=$((failed + 1))
        else
            skipped=$((skipped + 1))
        fi
    done
    
    echo
    echo "Summary: $total total, $passed passed, $failed failed, $skipped skipped"
    
    if [ $failed -eq 0 ]; then
        log_info "🎉 All tests passed!"
        return 0
    else
        log_error "❌ Some tests failed!"
        return 1
    fi
}

# Main function
main() {
    echo "🧪 Running tests for all services"
    echo "================================="
    echo
    
    # Check if infrastructure is running
    if ! docker exec ai-project-postgres pg_isready -U postgres &>/dev/null; then
        log_error "PostgreSQL is not running. Please start infrastructure services first:"
        log_error "docker compose -f docker-compose.dev.yml up -d"
        exit 1
    fi
    
    setup_test_database
    
    # Run tests for all services
    test_python_service "auth"
    test_python_service "profile"
    test_go_service
    test_python_service "notifications"
    test_node_service
    test_python_service "analytics"
    # Note: content-worker is a Celery worker, tests are part of content service
    
    show_results
}

main "$@"
