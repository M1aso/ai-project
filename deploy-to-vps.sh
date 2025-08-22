#!/bin/bash

set -e

# VPS Configuration
VPS_IP="45.146.164.70"
VPS_HOST="45.146.164.70.nip.io"
NAMESPACE="dev"

echo "🚀 Deploying to VPS: $VPS_IP"
echo "📍 Host: $VPS_HOST"
echo "📦 Namespace: $NAMESPACE"
echo

# Services to deploy
SERVICES=("auth" "profile" "content" "content-worker" "notifications" "chat" "analytics")

echo "📋 Services to deploy: ${SERVICES[*]}"
echo

# Function to deploy a service
deploy_service() {
    local service=$1
    echo "🔄 Deploying $service..."
    
    if [ -f "deploy/helm/$service/values.prod.yaml" ]; then
        helm upgrade --install "$service" "deploy/helm/$service" \
            --namespace "$NAMESPACE" \
            --create-namespace \
            -f "deploy/helm/$service/values.prod.yaml" \
            --wait \
            --timeout=300s
        echo "✅ $service deployed successfully"
    else
        echo "❌ No production values found for $service"
        return 1
    fi
}

# Deploy API Gateway first
echo "🌐 Deploying API Gateway..."
helm upgrade --install api-gateway deploy/helm/api-gateway \
    --namespace "$NAMESPACE" \
    --create-namespace \
    -f deploy/helm/api-gateway/values.prod.yaml \
    --wait \
    --timeout=300s

echo "✅ API Gateway deployed successfully"
echo

# Deploy all microservices
for service in "${SERVICES[@]}"; do
    deploy_service "$service"
    echo
done

echo "🎉 All services deployed!"
echo
echo "📊 Checking deployment status..."
kubectl -n "$NAMESPACE" get pods
echo
echo "🌍 Your application should be available at:"
echo "  http://$VPS_HOST/api/auth/healthz"
echo "  http://$VPS_HOST/api/profile/healthz"
echo "  http://$VPS_HOST/api/content/healthz"
echo
echo "🔍 To check logs for a specific service:"
echo "  kubectl -n $NAMESPACE logs -l app=SERVICE_NAME"
echo
echo "🔧 To troubleshoot:"
echo "  kubectl -n $NAMESPACE describe pod POD_NAME"