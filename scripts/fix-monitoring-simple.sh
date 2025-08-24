#!/bin/bash

# Simple script to apply monitoring ingress without sudo requirements
# This assumes kubeconfig is already properly configured

set -euo pipefail

echo "🚀 Applying monitoring ingress resources"

# Set kubeconfig if it exists
if [ -f ~/.kube/config ]; then
    export KUBECONFIG=~/.kube/config
elif [ -f /etc/rancher/k3s/k3s.yaml ]; then
    export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
fi

# Apply the monitoring ingress
echo "Applying monitoring ingress..."
kubectl apply -f deploy/k8s/monitoring-ingress.yaml

echo "Waiting for ingress to be ready..."
sleep 10

echo "Checking ingress status:"
kubectl get ingress -n monitoring
kubectl get ingress -n rabbitmq

echo "✅ Monitoring ingress applied successfully!"

echo ""
echo "🌐 Test these URLs:"
echo "• Grafana: http://grafana.45.146.164.70.nip.io"
echo "• Prometheus: http://prometheus.45.146.164.70.nip.io"
echo "• RabbitMQ: http://rabbitmq.45.146.164.70.nip.io"
