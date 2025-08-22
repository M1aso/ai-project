#!/bin/bash

# Quick fix script for VPS deployment issues
# Run this directly on your VPS: ssh root@45.146.164.70

set -e

echo "🔧 Quick Fix for VPS Deployment Issues"
echo "======================================"

# Set up environment
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
NAMESPACE="dev"

echo "📋 Current pod status:"
kubectl -n "$NAMESPACE" get pods
echo

echo "🗑️  Cleaning up broken deployments..."
kubectl -n "$NAMESPACE" delete deployment --all --ignore-not-found=true
echo "✅ Broken deployments removed"
echo

echo "🐳 Installing Docker for local image building..."
if ! command -v docker &> /dev/null; then
    apt-get update
    apt-get install -y docker.io
    systemctl start docker
    systemctl enable docker
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi
echo

echo "📦 Installing Git..."
if ! command -v git &> /dev/null; then
    apt-get install -y git
    echo "✅ Git installed"
else
    echo "✅ Git already installed"
fi
echo

echo "📥 Cloning repository..."
if [ ! -d "microservices-platform" ]; then
    git clone https://github.com/M1aso/microservices-platform.git
    cd microservices-platform
else
    cd microservices-platform
    git pull
fi
echo "✅ Repository ready"
echo

echo "🔨 Building Docker images locally..."
SERVICES=("auth" "profile" "content" "notifications" "chat" "analytics")

for service in "${SERVICES[@]}"; do
    if [ -f "services/$service/Dockerfile" ]; then
        echo "Building $service..."
        docker build -t "ghcr.io/m1aso/$service:latest" "services/$service"
        echo "✅ $service image built"
    else
        echo "⚠️  No Dockerfile found for $service"
    fi
done
echo

echo "🚀 Deploying services with local images..."

# Deploy auth service
if [ -f "deploy/helm/auth/Chart.yaml" ]; then
    helm upgrade --install auth deploy/helm/auth \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --set image.repository="ghcr.io/m1aso/auth" \
        --set image.tag="latest" \
        --set image.pullPolicy="Never" \
        --set imagePullSecrets=null \
        --wait --timeout=300s
    echo "✅ Auth service deployed"
fi

# Deploy other services
for service in "profile" "content" "notifications" "chat" "analytics"; do
    if [ -f "deploy/helm/$service/Chart.yaml" ]; then
        helm upgrade --install "$service" "deploy/helm/$service" \
            --namespace "$NAMESPACE" \
            --create-namespace \
            --set image.repository="ghcr.io/m1aso/$service" \
            --set image.tag="latest" \
            --set image.pullPolicy="Never" \
            --set imagePullSecrets=null \
            --wait --timeout=300s
        echo "✅ $service service deployed"
    fi
done

# Deploy API Gateway
if [ -f "deploy/helm/api-gateway/Chart.yaml" ]; then
    helm upgrade --install api-gateway deploy/helm/api-gateway \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --set ingress.host="45.146.164.70.nip.io" \
        --wait --timeout=300s
    echo "✅ API Gateway deployed"
fi

echo
echo "📊 Final deployment status:"
kubectl -n "$NAMESPACE" get pods
echo
echo "🌍 Testing endpoints..."
sleep 10  # Wait for pods to be ready

curl -s -o /dev/null -w "Auth health check: %{http_code}\n" http://45.146.164.70.nip.io/api/auth/healthz || echo "Auth service not ready yet"
curl -s -o /dev/null -w "Profile health check: %{http_code}\n" http://45.146.164.70.nip.io/api/profile/healthz || echo "Profile service not ready yet"

echo
echo "🎉 Deployment completed!"
echo "📱 Your application is available at: http://45.146.164.70.nip.io"
echo
echo "🔍 To check logs:"
echo "  kubectl -n $NAMESPACE logs -l app=SERVICE_NAME"
echo
echo "📊 To monitor pods:"
echo "  kubectl -n $NAMESPACE get pods -w"