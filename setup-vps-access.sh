#!/bin/bash

echo "🔧 Setting up VPS Access for GitHub Actions"
echo "=========================================="

VPS_IP="45.146.164.70"

echo "📋 Step 1: Generate SSH key for GitHub Actions"
echo "Run this on your LOCAL machine:"
echo
echo "ssh-keygen -t ed25519 -f ~/.ssh/github-actions-vps -N ''"
echo "cat ~/.ssh/github-actions-vps.pub"
echo
echo "📋 Step 2: Add public key to VPS"
echo "Copy the public key output above, then run on VPS:"
echo
echo "ssh root@$VPS_IP"
echo "mkdir -p ~/.ssh"
echo "echo 'PASTE_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys"
echo "chmod 700 ~/.ssh"
echo "chmod 600 ~/.ssh/authorized_keys"
echo
echo "📋 Step 3: Test SSH connection"
echo "ssh -i ~/.ssh/github-actions-vps root@$VPS_IP"
echo
echo "📋 Step 4: Add secrets to GitHub repository"
echo "Go to: https://github.com/M1aso/ai-project/settings/secrets/actions"
echo "Add these secrets:"
echo "  - SSH_HOST: $VPS_IP"
echo "  - SSH_USERNAME: root"
echo "  - SSH_PRIVATE_KEY: (content of ~/.ssh/github-actions-vps)"
echo "  - GHCR_USERNAME: M1aso"
echo "  - GHCR_TOKEN: (your GitHub personal access token)"
echo
echo "📋 Step 5: Create kubeconfig secret"
echo "On VPS, run:"
echo "cat /etc/rancher/k3s/k3s.yaml | base64 -w 0"
echo "Add the output as KUBE_CONFIG secret in GitHub"