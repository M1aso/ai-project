#!/bin/bash

# Environment Management Script for AI Project
# Usage: ./manage-env.sh [command] [environment] [service] [options]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_cmd() { echo -e "${BLUE}[CMD]${NC} $1"; }

show_help() {
    cat << EOF
Environment Management Script for AI Project

USAGE:
    $0 [COMMAND] [ENVIRONMENT] [SERVICE] [OPTIONS]

COMMANDS:
    list        List environment variables for a service
    set         Set an environment variable
    get         Get a specific environment variable
    update      Update environment variables from file
    secrets     Manage Kubernetes secrets
    deploy      Redeploy service after env changes
    show        Show all environments and services

ENVIRONMENTS:
    dev         Development environment
    staging     Staging environment  
    prod        Production environment

SERVICES:
    auth, profile, content, notifications, chat, analytics, content-worker, api-gateway, swagger-ui

EXAMPLES:
    # List all env vars for auth service in dev
    $0 list dev auth

    # Set a single environment variable
    $0 set dev auth LOG_LEVEL DEBUG

    # Get specific environment variable
    $0 get dev auth DATABASE_URL

    # Update from values file and redeploy
    $0 update dev auth

    # Create/update secrets
    $0 secrets dev auth JWT_SECRET my-secret-key

    # Redeploy service
    $0 deploy dev auth

    # Show all environments
    $0 show

EOF
}

validate_params() {
    local cmd=$1
    local env=${2:-}
    local svc=${3:-}
    
    if [[ ! "$cmd" =~ ^(list|set|get|update|secrets|deploy|show)$ ]]; then
        log_error "Invalid command: $cmd"
        show_help
        exit 1
    fi
    
    if [[ "$cmd" != "show" && -z "$env" ]]; then
        log_error "Environment is required"
        show_help
        exit 1
    fi
    
    if [[ "$cmd" != "show" && ! "$env" =~ ^(dev|staging|prod)$ ]]; then
        log_error "Invalid environment: $env. Use: dev, staging, prod"
        exit 1
    fi
    
    if [[ "$cmd" =~ ^(list|set|get|update|secrets|deploy)$ && -z "$svc" ]]; then
        log_error "Service is required for command: $cmd"
        show_help
        exit 1
    fi
    
    if [[ -n "$svc" && ! "$svc" =~ ^(auth|profile|content|notifications|chat|analytics|content-worker|api-gateway|swagger-ui)$ ]]; then
        log_error "Invalid service: $svc"
        exit 1
    fi
}

list_env_vars() {
    local env=$1
    local svc=$2
    
    log_info "Environment variables for $svc in $env environment:"
    echo "=================================================="
    
    # Check if values file exists
    local values_file="deploy/helm/$svc/values.$env.yaml"
    if [[ -f "$values_file" ]]; then
        echo "📁 From values file: $values_file"
        yq eval '.env[]' "$values_file" 2>/dev/null || echo "No env section found"
        echo ""
    fi
    
    # Check deployed environment variables
    if kubectl get deployment "$svc" -n "$env" &>/dev/null; then
        echo "🚀 Currently deployed:"
        kubectl get deployment "$svc" -n "$env" -o jsonpath='{.spec.template.spec.containers[0].env[*]}' | jq -r '.name + " = " + (.value // .valueFrom | tostring)'
    else
        log_warn "Service $svc not deployed in $env environment"
    fi
}

set_env_var() {
    local env=$1
    local svc=$2
    local var_name=$3
    local var_value=$4
    
    log_info "Setting $var_name=$var_value for $svc in $env"
    
    # Update via Helm
    helm upgrade "$svc" "deploy/helm/$svc" \
        --namespace "$env" \
        --set "env[0].name=$var_name" \
        --set "env[0].value=$var_value" \
        --reuse-values
    
    log_info "Environment variable updated. Service will restart automatically."
}

get_env_var() {
    local env=$1
    local svc=$2
    local var_name=$3
    
    if kubectl get deployment "$svc" -n "$env" &>/dev/null; then
        local value=$(kubectl get deployment "$svc" -n "$env" -o jsonpath="{.spec.template.spec.containers[0].env[?(@.name=='$var_name')].value}")
        if [[ -n "$value" ]]; then
            echo "$var_name=$value"
        else
            log_warn "Environment variable $var_name not found for $svc in $env"
        fi
    else
        log_error "Service $svc not found in $env environment"
    fi
}

update_from_file() {
    local env=$1
    local svc=$2
    
    local values_file="deploy/helm/$svc/values.$env.yaml"
    if [[ ! -f "$values_file" ]]; then
        log_error "Values file not found: $values_file"
        exit 1
    fi
    
    log_info "Updating $svc in $env from $values_file"
    
    helm upgrade "$svc" "deploy/helm/$svc" \
        --namespace "$env" \
        -f "$values_file"
    
    log_info "Service updated successfully"
}

manage_secrets() {
    local env=$1
    local svc=$2
    local secret_name=${3:-}
    local secret_value=${4:-}
    
    if [[ -z "$secret_name" ]]; then
        # List secrets
        log_info "Secrets for $svc in $env:"
        kubectl get secrets -n "$env" | grep "$svc" || log_warn "No secrets found for $svc"
        return
    fi
    
    if [[ -z "$secret_value" ]]; then
        log_error "Secret value is required"
        exit 1
    fi
    
    # Create or update secret
    local secret_resource="$svc-secrets"
    
    kubectl create secret generic "$secret_resource" \
        --namespace="$env" \
        --from-literal="$secret_name=$secret_value" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_info "Secret $secret_name created/updated for $svc in $env"
}

deploy_service() {
    local env=$1
    local svc=$2
    
    log_info "Deploying $svc to $env environment"
    
    local values_file="deploy/helm/$svc/values.$env.yaml"
    if [[ -f "$values_file" ]]; then
        EXTRA_VALUES=(-f "$values_file")
    else
        EXTRA_VALUES=()
    fi
    
    if [[ "$svc" = "swagger-ui" ]]; then
        helm upgrade --install "$svc" "deploy/helm/$svc" \
            --namespace "$env" --create-namespace \
            "${EXTRA_VALUES[@]}"
    else
        helm upgrade --install "$svc" "deploy/helm/$svc" \
            --namespace "$env" --create-namespace \
            --set "image.repository=ghcr.io/m1aso/$svc" \
            --set "image.tag=latest" \
            "${EXTRA_VALUES[@]}"
    fi
    
    log_info "Deployment completed"
}

show_all() {
    echo "🌍 AI Project Environments Overview"
    echo "==================================="
    echo ""
    
    for env in dev staging prod; do
        echo "📂 Environment: $env"
        echo "  Namespace: $env"
        if kubectl get namespace "$env" &>/dev/null; then
            echo "  Status: ✅ Active"
            echo "  Services:"
            kubectl get deployments -n "$env" --no-headers 2>/dev/null | awk '{print "    • " $1}' || echo "    No deployments"
        else
            echo "  Status: ❌ Not created"
        fi
        echo ""
    done
    
    echo "🔧 Infrastructure Services:"
    echo "=========================="
    echo "• PostgreSQL: $(kubectl get pods -n postgresql --no-headers 2>/dev/null | wc -l) pods"
    echo "• Redis: $(kubectl get pods -n redis --no-headers 2>/dev/null | wc -l) pods"
    echo "• RabbitMQ: $(kubectl get pods -n rabbitmq --no-headers 2>/dev/null | wc -l) pods"
    echo "• MinIO: $(kubectl get pods -n minio --no-headers 2>/dev/null | wc -l) pods"
    echo "• Monitoring: $(kubectl get pods -n monitoring --no-headers 2>/dev/null | wc -l) pods"
}

# Main script logic
main() {
    local cmd=${1:-}
    local env=${2:-}
    local svc=${3:-}
    local arg1=${4:-}
    local arg2=${5:-}
    
    if [[ -z "$cmd" ]]; then
        show_help
        exit 0
    fi
    
    validate_params "$cmd" "$env" "$svc"
    
    case "$cmd" in
        list)
            list_env_vars "$env" "$svc"
            ;;
        set)
            if [[ -z "$arg1" || -z "$arg2" ]]; then
                log_error "Usage: $0 set <env> <service> <var_name> <var_value>"
                exit 1
            fi
            set_env_var "$env" "$svc" "$arg1" "$arg2"
            ;;
        get)
            if [[ -z "$arg1" ]]; then
                log_error "Usage: $0 get <env> <service> <var_name>"
                exit 1
            fi
            get_env_var "$env" "$svc" "$arg1"
            ;;
        update)
            update_from_file "$env" "$svc"
            ;;
        secrets)
            manage_secrets "$env" "$svc" "$arg1" "$arg2"
            ;;
        deploy)
            deploy_service "$env" "$svc"
            ;;
        show)
            show_all
            ;;
        *)
            log_error "Unknown command: $cmd"
            show_help
            exit 1
            ;;
    esac
}

# Check if required tools are available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is required but not installed"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    log_error "helm is required but not installed"
    exit 1
fi

main "$@"