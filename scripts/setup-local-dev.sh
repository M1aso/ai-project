#!/bin/bash

# Local Development Setup Script
# This script sets up the complete local development environment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check Go
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed. Please install Go 1.21+ first."
        exit 1
    fi
    
    log_info "All prerequisites are installed ✓"
}

# Start infrastructure services
start_infrastructure() {
    log_step "Starting infrastructure services..."
    
    # Stop any existing containers
    docker compose -f docker-compose.dev.yml down 2>/dev/null || true
    
    # Start infrastructure services
    docker compose -f docker-compose.dev.yml up -d
    
    log_info "Infrastructure services started"
    log_info "Waiting for services to be ready..."
    
    # Wait for services to be healthy
    sleep 30
    
    # Check if services are healthy
    if docker compose -f docker-compose.dev.yml ps | grep -q "unhealthy"; then
        log_warn "Some infrastructure services are not healthy. Continuing anyway..."
        docker compose -f docker-compose.dev.yml ps
    else
        log_info "All infrastructure services are healthy ✓"
    fi
}

# Setup Python services
setup_python_service() {
    local service_name=$1
    local port=$2
    
    log_step "Setting up $service_name service..."
    
    cd "services/$service_name"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Created virtual environment for $service_name"
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create start script
    cat > start-dev.sh << EOF
#!/bin/bash
source venv/bin/activate

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export RABBITMQ_URL="amqp://admin:admin123@localhost:5672"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export JWT_SECRET="local-dev-jwt-secret-not-for-production"
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
export REFRESH_TOKEN_EXPIRE_DAYS="30"
export LOG_LEVEL="DEBUG"

# Run database migrations
if [ -f "alembic.ini" ]; then
    alembic upgrade head
fi

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port $port --reload
EOF
    
    chmod +x start-dev.sh
    
    cd ../..
    log_info "$service_name service setup complete"
}

# Setup Chat service (Node.js)
setup_chat_service() {
    log_step "Setting up chat service..."
    
    cd services/chat
    
    # Install dependencies
    npm install
    
    # Build TypeScript
    npm run build
    
    # Create start script
    cat > start-dev.sh << 'EOF'
#!/bin/bash

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"
export PORT="8005"

# Run database migrations (if any)
# npm run migrate

# Start the service in development mode
npm run dev
EOF
    
    chmod +x start-dev.sh
    
    cd ../..
    log_info "Chat service setup complete"
}

# Setup Content service (Go)
setup_content_service() {
    log_step "Setting up content service..."
    
    cd services/content
    
    # Download dependencies
    go mod download
    
    # Create start script
    cat > start-dev.sh << 'EOF'
#!/bin/bash

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"
export PORT="8003"

# Run database migrations (if any)
# go run internal/db/migrations/migrate.go

# Start the service in development mode
go run cmd/server/main.go
EOF
    
    chmod +x start-dev.sh
    
    cd ../..
    log_info "Content service setup complete"
}

# Setup Content Worker service
setup_content_worker_service() {
    log_step "Setting up content-worker service..."
    
    cd services/content-worker
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_info "Created virtual environment for content-worker"
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create start script
    cat > start-dev.sh << 'EOF'
#!/bin/bash
source venv/bin/activate

# Set environment variables
export DATABASE_URL="postgresql://postgres:postgres123@localhost:5432/aiproject"
export REDIS_URL="redis://localhost:6379"
export RABBITMQ_URL="amqp://admin:admin123@localhost:5672"
export MINIO_ENDPOINT="localhost:9000"
export MINIO_ACCESS_KEY="admin"
export MINIO_SECRET_KEY="admin123456"
export MINIO_SECURE="false"
export LOG_LEVEL="DEBUG"

# Start the worker
python app/worker.py
EOF
    
    chmod +x start-dev.sh
    
    cd ../..
    log_info "Content-worker service setup complete"
}

# Create global helper scripts
create_helper_scripts() {
    log_step "Creating helper scripts..."
    
    # Create wait-for-services script
    cat > scripts/wait-for-services.sh << 'EOF'
#!/bin/bash

echo "Waiting for infrastructure services to be ready..."

# Wait for PostgreSQL
echo -n "Waiting for PostgreSQL..."
until docker exec ai-project-postgres pg_isready -U postgres -d aiproject &>/dev/null; do
    echo -n "."
    sleep 2
done
echo " ✓"

# Wait for Redis
echo -n "Waiting for Redis..."
until docker exec ai-project-redis redis-cli ping &>/dev/null; do
    echo -n "."
    sleep 2
done
echo " ✓"

# Wait for RabbitMQ
echo -n "Waiting for RabbitMQ..."
until docker exec ai-project-rabbitmq rabbitmq-diagnostics ping &>/dev/null; do
    echo -n "."
    sleep 2
done
echo " ✓"

# Wait for MinIO
echo -n "Waiting for MinIO..."
until curl -f http://localhost:9000/minio/health/live &>/dev/null; do
    echo -n "."
    sleep 2
done
echo " ✓"

echo "All infrastructure services are ready!"
EOF
    
    # Create check-services script
    cat > scripts/check-services.sh << 'EOF'
#!/bin/bash

echo "🔍 Checking service status..."
echo

# Infrastructure services
echo "📦 Infrastructure Services:"
echo "=========================="
docker compose -f docker-compose.dev.yml ps

echo
echo "📚 Application Services:"
echo "======================="

services=("auth:8001" "profile:8002" "content:8003" "notifications:8004" "chat:8005" "analytics:8006")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    if curl -s -f "http://localhost:$port/healthz" >/dev/null 2>&1; then
        echo "✅ $name service (port $port): Running"
    else
        echo "❌ $name service (port $port): Not running"
    fi
done

echo
echo "🌐 Access URLs:"
echo "=============="
echo "• API Gateway: http://localhost:8080"
echo "• MinIO Console: http://localhost:9001 (admin/admin123456)"
echo "• RabbitMQ Management: http://localhost:15672 (admin/admin123)"
echo "• Grafana: http://localhost:3000 (admin/admin123)"
echo "• Prometheus: http://localhost:9090"
EOF
    
    # Create start-all-services script
    cat > scripts/start-all-services.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting all services..."

# Start infrastructure first
docker compose -f docker-compose.dev.yml up -d
./scripts/wait-for-services.sh

echo
echo "Starting application services..."
echo "Note: Run each service in a separate terminal for better debugging:"
echo

services=("auth" "profile" "content" "notifications" "chat" "analytics" "content-worker")

for service in "${services[@]}"; do
    echo "# Terminal for $service service:"
    echo "cd services/$service && ./start-dev.sh"
    echo
done

echo "Or use tmux/screen to run all services:"
echo "./scripts/start-services-tmux.sh"
EOF
    
    # Create stop-all-services script
    cat > scripts/stop-all-services.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping all services..."

# Stop infrastructure services
docker compose -f docker-compose.dev.yml down

# Kill any running application services
echo "Killing application services on ports 8001-8006..."
for port in {8001..8006}; do
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
done

echo "All services stopped."
EOF
    
    # Make all scripts executable
    chmod +x scripts/wait-for-services.sh
    chmod +x scripts/check-services.sh
    chmod +x scripts/start-all-services.sh
    chmod +x scripts/stop-all-services.sh
    
    log_info "Helper scripts created"
}

# Main setup function
main() {
    echo "🚀 AI Project - Local Development Setup"
    echo "======================================"
    echo
    
    check_prerequisites
    start_infrastructure
    
    # Setup all services
    setup_python_service "auth" "8001"
    setup_python_service "profile" "8002"
    setup_content_service
    setup_python_service "notifications" "8004"
    setup_chat_service
    setup_python_service "analytics" "8006"
    setup_content_worker_service
    
    create_helper_scripts
    
    echo
    log_info "🎉 Local development environment setup complete!"
    echo
    echo "📋 Next steps:"
    echo "=============="
    echo "1. Wait for infrastructure services to be fully ready:"
    echo "   ./scripts/wait-for-services.sh"
    echo
    echo "2. Start application services (in separate terminals):"
    echo "   cd services/auth && ./start-dev.sh"
    echo "   cd services/profile && ./start-dev.sh"
    echo "   cd services/content && ./start-dev.sh"
    echo "   cd services/notifications && ./start-dev.sh"
    echo "   cd services/chat && ./start-dev.sh"
    echo "   cd services/analytics && ./start-dev.sh"
    echo "   cd services/content-worker && ./start-dev.sh"
    echo
    echo "3. Check service status:"
    echo "   ./scripts/check-services.sh"
    echo
    echo "4. Access the API Gateway:"
    echo "   http://localhost:8080"
    echo
    echo "📖 For detailed instructions, see LOCAL_DEVELOPMENT_GUIDE.md"
}

# Run main function
main "$@"
