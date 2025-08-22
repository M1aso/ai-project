#!/bin/bash

set -e

# Configuration
REGISTRY="ghcr.io"
OWNER="m1aso"  # lowercase as required by GHCR
TAG="${1:-dev}"

# Services to build
SERVICES=("auth" "profile" "content" "content-worker" "notifications" "chat" "analytics")

echo "Building and pushing Docker images..."
echo "Registry: $REGISTRY"
echo "Owner: $OWNER"
echo "Tag: $TAG"
echo

# Login to GHCR (you'll need to provide your token)
echo "Please ensure you're logged into GHCR:"
echo "docker login ghcr.io -u M1aso -p YOUR_GITHUB_TOKEN"
echo

# Build and push each service
for service in "${SERVICES[@]}"; do
    echo "Building $service..."
    
    if [ -f "services/$service/Dockerfile" ]; then
        docker build -t "$REGISTRY/$OWNER/$service:$TAG" "services/$service"
        docker push "$REGISTRY/$OWNER/$service:$TAG"
        echo "✅ Successfully built and pushed $service"
    else
        echo "❌ No Dockerfile found for $service"
    fi
    echo
done

echo "All images built and pushed successfully!"
echo
echo "To deploy to your VPS, use these image tags in your Helm values:"
for service in "${SERVICES[@]}"; do
    echo "  $service: $REGISTRY/$OWNER/$service:$TAG"
done