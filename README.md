# AI E-Learning Platform

A comprehensive microservices-based e-learning platform featuring authentication, content management, real-time chat, notifications, and analytics.

## 🚨 SECURITY WARNING

**CRITICAL SECURITY VULNERABILITIES IDENTIFIED (2025-08-26)**

⚠️ **Content Service** and **Analytics Service** are currently **UNPROTECTED** - anyone can access/modify data without authentication. See [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md) for details.

**DO NOT USE IN PRODUCTION** until security fixes are implemented.

## 🚀 Quick Start

**Get your platform running in 15 minutes:**

1. **Setup VPS** (5 min): Run `./scripts/setup-vps.sh dev` on your VPS
2. **Configure GitHub** (3 min): Add secrets for CI/CD  
3. **Deploy** (2 min): Push to `dev` branch for auto-deployment
4. **Access** (1 min): Visit http://api.45.146.164.70.nip.io

👉 **[Complete Quick Start Guide](QUICK_START.md)**

## 🏗️ Architecture

### Microservices
- **Auth Service**: Phone/email authentication, JWT tokens
- **Profile Service**: User profiles, avatar management  
- **Content Service**: Course content, video processing
- **Notifications Service**: Email/SMS/Telegram notifications
- **Chat Service**: Real-time messaging, file sharing
- **Analytics Service**: Metrics, reporting, dashboards
- **Content Worker**: Background video transcoding

### Infrastructure
- **API Gateway**: Envoy proxy with JWT validation
- **Database**: PostgreSQL with migrations
- **Storage**: MinIO for files and media
- **Cache**: Redis for sessions and caching
- **Queue**: RabbitMQ for async processing
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Kubernetes + Helm

## 🌐 Environments

| Environment | VPS | Domain | Branch/Tag | Deployment |
|-------------|-----|--------|------------|------------|
| **Dev** | 45.146.164.70 | `*.45.146.164.70.nip.io` | `dev` branch | Auto on push |
| **Staging** | 45.146.164.70 | `*.staging.45.146.164.70.nip.io` | `main` branch | Manual |
| **Prod** | TBD | `*.yourdomain.com` | `release-*` tags | Auto on tag |

## 📡 Service Endpoints

### Application APIs
- **🌐 API Gateway**: http://api.45.146.164.70.nip.io
- **📚 API Documentation**: http://docs.45.146.164.70.nip.io
- **🔐 Auth API**: http://api.45.146.164.70.nip.io/api/auth
- **👤 Profile API**: http://api.45.146.164.70.nip.io/api/profile
- **📖 Content API**: http://api.45.146.164.70.nip.io/api/content
- **🔔 Notifications API**: http://api.45.146.164.70.nip.io/api/notifications
- **💬 Chat API**: http://api.45.146.164.70.nip.io/api/chat
- **📊 Analytics API**: http://api.45.146.164.70.nip.io/api/analytics

## 📚 API Documentation

Each service now **dynamically generates** its OpenAPI specification and exposes it at `/api/{service}/openapi.json` with Swagger UI at `/api/{service}/docs`.

**Centralized Documentation**: All services are available at [http://docs.45.146.164.70.nip.io](http://docs.45.146.164.70.nip.io) with live, always-up-to-date API specs.

**Benefits:**
- ✅ **Zero maintenance** - documentation automatically syncs with code
- ✅ **Always accurate** - no more outdated YAML files
- ✅ **Professional UI** - categorized endpoints with proper examples
- ✅ **Interactive testing** - test APIs directly from documentation

### Infrastructure Services
- **📊 Grafana**: http://grafana.45.146.164.70.nip.io (admin/admin123)
- **💾 MinIO Console**: http://minio.45.146.164.70.nip.io (admin/admin123456)
- **🐰 RabbitMQ**: http://rabbitmq.45.146.164.70.nip.io (admin/admin123)
- **📈 Prometheus**: http://prometheus.45.146.164.70.nip.io

## 🛠️ Development Workflow

### Making Changes
```bash
# Create feature branch from dev
git checkout dev && git pull origin dev
git checkout -b feature/my-feature

# Make changes, commit, and push
git add . && git commit -m "feat: my feature"
git push origin feature/my-feature

# Create PR to dev → Auto-deploy after merge
```

### Production Release
```bash
# Create release tag from main
git checkout main && git pull origin main
git tag release-1.0.0 && git push origin release-1.0.0
# → Auto-deploy to production
```

## 📖 Documentation

- **[🚀 Quick Start Guide](QUICK_START.md)**: Get running in 15 minutes
- **[🏗️ Deployment Guide](DEPLOYMENT.md)**: Complete VPS setup instructions
- **[🔧 Environment Reference](ENV_REFERENCE.md)**: Environment variables guide
- **[📋 Requirements](REQUIREMENTS.md)**: Detailed project requirements
- **[🤖 Agents Guide](AGENTS.md)**: AI development workflow

## 🔧 Management Scripts

```bash
# VPS setup (run once)
./scripts/setup-vps.sh dev

# Environment management
./scripts/manage-env.sh list dev auth          # List env vars
./scripts/manage-env.sh set dev auth LOG_LEVEL DEBUG  # Set env var
./scripts/manage-env.sh deploy dev auth        # Redeploy service
./scripts/manage-env.sh show                   # Overview
```

## 🏃‍♂️ Common Operations

```bash
# Check service status
kubectl get pods -A

# View logs
kubectl logs -f deployment/auth -n dev

# Scale service
kubectl scale deployment auth --replicas=3 -n dev

# Test API
curl http://api.45.146.164.70.nip.io/api/auth/healthz
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **Role-Based Access**: Granular permissions
- **TLS/SSL**: HTTPS in production
- **Secrets Management**: Kubernetes secrets for sensitive data
- **Network Policies**: Service isolation
- **Regular Backups**: Automated database backups

## 📊 Monitoring & Observability

- **Metrics**: Prometheus metrics for all services
- **Dashboards**: Pre-configured Grafana dashboards
- **Logging**: Centralized logging with kubectl
- **Health Checks**: `/healthz` and `/readyz` endpoints
- **Alerts**: Configurable alerting rules

## 🤝 Contributing

1. Fork the repository
2. Create feature branch from `dev`
3. Make changes and test locally
4. Create PR to `dev` branch
5. After merge, changes auto-deploy to dev environment

## 📞 Support

- **Documentation**: Check the docs folder
- **Issues**: Create GitHub issues
- **Monitoring**: Check Grafana dashboards
- **Logs**: Use `kubectl logs` commands

---

**🎯 Project Status**: ⚠️ CRITICAL SECURITY ISSUES IDENTIFIED  
**🚀 Last Updated**: 2025-08-26  
**📚 API Docs**: http://docs.45.146.164.70.nip.io  
**🔒 Security Report**: [SECURITY_AUDIT_REPORT.md](SECURITY_AUDIT_REPORT.md)  
**👨‍💻 Developer Guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
# Test improved workflows
