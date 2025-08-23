#!/bin/bash

# Run database migrations for all services
# This script should be run after the infrastructure is ready

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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

# Check if PostgreSQL is ready
check_postgres() {
    log_info "Checking PostgreSQL connection..."
    if ! docker exec ai-project-postgres pg_isready -U postgres -d aiproject &>/dev/null; then
        log_error "PostgreSQL is not ready. Please start infrastructure services first:"
        log_error "docker compose -f docker-compose.dev.yml up -d"
        exit 1
    fi
    log_info "PostgreSQL is ready ✓"
}

# Run migrations for Python services
run_python_migrations() {
    local service_name=$1
    
    log_info "Running migrations for $service_name service..."
    
    cd "services/$service_name"
    
    if [ -f "alembic.ini" ]; then
        if [ -d "venv" ]; then
            source venv/bin/activate
            export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
            alembic upgrade head
            log_info "$service_name migrations completed ✓"
        else
            log_warn "$service_name: Virtual environment not found. Run setup first."
        fi
    else
        log_warn "$service_name: No alembic.ini found, skipping migrations"
    fi
    
    cd ../..
}

# Run migrations for Go service
run_go_migrations() {
    log_info "Running migrations for content service..."
    
    cd services/content
    
    export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
    
    # Check if migration script exists
    if [ -f "internal/db/migrations/migrate.go" ]; then
        go run internal/db/migrations/migrate.go
        log_info "Content service migrations completed ✓"
    else
        log_warn "Content service: No migration script found, skipping migrations"
    fi
    
    cd ../..
}

# Run migrations for Node.js service
run_node_migrations() {
    log_info "Running migrations for chat service..."
    
    cd services/chat
    
    export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
    
    # Check if migration script exists in package.json
    if npm run | grep -q "migrate"; then
        npm run migrate
        log_info "Chat service migrations completed ✓"
    else
        log_warn "Chat service: No migrate script found, skipping migrations"
    fi
    
    cd ../..
}

# Main function
main() {
    echo "🗃️ Running database migrations for all services"
    echo "=============================================="
    echo
    
    check_postgres
    
    # Run migrations for all services
    run_python_migrations "auth"
    run_python_migrations "profile"
    run_go_migrations
    run_python_migrations "notifications"
    run_node_migrations
    run_python_migrations "analytics"
    
    echo
    log_info "🎉 All migrations completed successfully!"
    echo
    echo "You can now start the application services:"
    echo "./scripts/start-all-services.sh"
}

main "$@"
