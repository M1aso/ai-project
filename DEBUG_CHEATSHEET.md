# 🔧 Debug Cheat Sheet

Quick reference for debugging the AI Project locally and in production.

## 🚀 Quick Start Commands

```bash
# Start everything locally
docker-compose -f docker-compose.dev.yml up -d

# Check all service status
docker-compose -f docker-compose.dev.yml ps

# View logs for all services
docker-compose -f docker-compose.dev.yml logs -f

# Stop everything
docker-compose -f docker-compose.dev.yml down
```

## 📊 Service Status Checks

### Local (Docker)
```bash
# Individual service logs
docker-compose -f docker-compose.dev.yml logs -f auth
docker-compose -f docker-compose.dev.yml logs -f chat
docker-compose -f docker-compose.dev.yml logs -f content

# Service health checks
curl http://localhost:8000/healthz  # Auth
curl http://localhost:8001/health   # Chat  
curl http://localhost:8002/health   # Content
curl http://localhost:8003/healthz  # Profile
curl http://localhost:8004/healthz  # Analytics
curl http://localhost:8005/healthz  # Notifications
```

### Production (Kubernetes)
```bash
# Pod status
kubectl get pods -n dev

# Service logs
kubectl logs -f deployment/auth -n dev
kubectl logs -f deployment/chat -n dev
kubectl logs -f deployment/content -n dev

# Service health
kubectl exec -n dev deployment/auth -- curl localhost:8000/healthz
```

## 🗄️ Database Debugging

### PostgreSQL
```bash
# Local connection
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -d aiproject

# Production connection (via SSH tunnel)
ssh -L 15432:localhost:5432 user@server
PGPASSWORD=prod_pass psql -h localhost -p 15432 -U postgres -d aiproject

# Useful queries
SELECT * FROM users ORDER BY created_at DESC LIMIT 5;
SELECT * FROM email_verifications WHERE expires_at > NOW();
SELECT COUNT(*) FROM users WHERE is_active = true;

# Check connections
SELECT pid, usename, application_name, client_addr, state 
FROM pg_stat_activity WHERE datname = 'aiproject';
```

### Redis
```bash
# Local connection
redis-cli -h localhost -p 6379

# Check keys
KEYS *
KEYS "rate_limit:*"
KEYS "login_attempts:*"

# Get values
GET "rate_limit:ip:127.0.0.1"
HGETALL "user_session:user123"

# Clear data (dev only!)
FLUSHALL

# Monitor commands
MONITOR
```

## 📨 Message Queue (RabbitMQ)

```bash
# Web UI
open http://localhost:15672  # admin/admin123

# CLI commands
rabbitmqctl list_queues name messages consumers
rabbitmqctl list_exchanges
rabbitmqctl list_bindings

# Purge queue (dev only!)
rabbitmqctl purge_queue user.registered
```

## 📧 Email Testing (MailHog)

```bash
# Web UI
open http://localhost:8025

# API check
curl http://localhost:8025/api/v2/messages | jq '.total'

# Clear all emails
curl -X DELETE http://localhost:8025/api/v1/messages
```

## 📁 File Storage (MinIO)

```bash
# Web console
open http://localhost:9001  # minioadmin/minioadmin123

# Health check
curl http://localhost:9000/minio/health/live

# List buckets via API
curl -X GET http://localhost:9000/
```

## 🔍 Common Debug Scenarios

### Registration Not Working

```bash
# 1. Check auth service logs
docker-compose -f docker-compose.dev.yml logs -f auth

# 2. Test database connection
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -d aiproject -c "SELECT 1"

# 3. Check SMTP (MailHog)
curl http://localhost:8025/api/v2/messages

# 4. Test registration manually
curl -X POST "http://localhost:8000/api/auth/email/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123!"}'

# 5. Check Redis rate limiting
redis-cli -h localhost -p 6379
KEYS "register:*"
```

### Chat Not Connecting

```bash
# 1. Check chat service
docker-compose -f docker-compose.dev.yml logs -f chat

# 2. Test WebSocket endpoint
curl -I http://localhost:8001/socket.io/

# 3. Check Redis connection
docker-compose -f docker-compose.dev.yml exec chat redis-cli -h redis -p 6379 ping
```

### File Upload Failing

```bash
# 1. Check content service
docker-compose -f docker-compose.dev.yml logs -f content

# 2. Test MinIO connection
curl http://localhost:9000/minio/health/live

# 3. Check bucket existence
docker-compose -f docker-compose.dev.yml exec minio mc ls local/

# 4. Test upload endpoint
curl -X POST "http://localhost:8002/api/content/upload" \
  -F "file=@test.jpg"
```

### Performance Issues

```bash
# 1. Check resource usage
docker stats

# 2. Database query performance
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -d aiproject
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

# 3. Redis memory usage
redis-cli -h localhost -p 6379 INFO memory

# 4. Check slow queries
docker-compose -f docker-compose.dev.yml logs auth | grep "slow query"
```

## 🎯 Production Debugging

### Pod Issues
```bash
# Pod not starting
kubectl describe pod auth-xxx-xxx -n dev
kubectl logs auth-xxx-xxx -n dev --previous

# Pod crashing
kubectl get events -n dev --sort-by='.lastTimestamp'
kubectl logs -f deployment/auth -n dev
```

### Service Issues
```bash
# Service not accessible
kubectl get svc -n dev
kubectl describe svc auth -n dev

# Endpoint issues
kubectl get endpoints -n dev
kubectl describe endpoints auth -n dev
```

### Network Issues
```bash
# Test pod-to-pod connectivity
kubectl exec -it auth-xxx-xxx -n dev -- nslookup redis-master.redis.svc.cluster.local
kubectl exec -it auth-xxx-xxx -n dev -- curl http://postgresql.postgresql.svc.cluster.local:5432

# Check ingress
kubectl get ingress -n dev
kubectl describe ingress api-ingress -n dev
```

### Resource Issues
```bash
# Check resource usage
kubectl top pods -n dev
kubectl top nodes

# Check resource limits
kubectl describe pod auth-xxx-xxx -n dev | grep -A 5 "Limits\|Requests"
```

## 📈 Monitoring Quick Checks

### Prometheus Queries
```promql
# Service availability
up{job="auth-service"}

# Request rate (last 5 minutes)
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Memory usage
container_memory_usage_bytes{pod=~"auth-.*"}

# Database connections
postgres_connections{database="aiproject"}
```

### Grafana Dashboards
- **AI Project Overview**: `/d/ai-project-overview`
- **Service Health**: Check green/red status indicators
- **Error Rates**: Look for spikes in error graphs
- **Response Times**: Check for latency increases

## 🛠️ Environment Variables Check

```bash
# Local services
docker-compose -f docker-compose.dev.yml exec auth env | grep -E "(DATABASE|REDIS|SMTP)"

# Production pods
kubectl exec -n dev deployment/auth -- env | grep -E "(DATABASE|REDIS|SMTP)"

# Check specific variable
kubectl exec -n dev deployment/auth -- printenv DATABASE_URL
```

## 🔄 Quick Fixes

### Reset Development Environment
```bash
# Nuclear option - reset everything
docker-compose -f docker-compose.dev.yml down -v
docker system prune -f
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
sleep 30

# Run migrations
./scripts/run-migrations.sh
```

### Clear Caches
```bash
# Clear Redis
redis-cli -h localhost -p 6379 FLUSHALL

# Clear RabbitMQ queues
rabbitmqctl purge_queue user.registered
rabbitmqctl purge_queue email.send

# Clear MailHog emails
curl -X DELETE http://localhost:8025/api/v1/messages
```

### Restart Specific Service
```bash
# Local
docker-compose -f docker-compose.dev.yml restart auth

# Production
kubectl rollout restart deployment/auth -n dev
kubectl rollout status deployment/auth -n dev
```

## 🆘 Emergency Commands

### Service Down
```bash
# Quick health check all services
for port in 8000 8001 8002 8003 8004 8005; do
  echo "Port $port: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health || echo "FAIL")"
done

# Restart all services
docker-compose -f docker-compose.dev.yml restart
```

### Database Issues
```bash
# Check if database is accepting connections
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -c "SELECT 1" 2>/dev/null && echo "DB OK" || echo "DB FAIL"

# Check database size
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -d aiproject -c "
SELECT pg_size_pretty(pg_database_size('aiproject')) as size;
"

# Kill all connections to database (emergency only!)
PGPASSWORD=postgres123 psql -h localhost -p 5432 -U postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE datname = 'aiproject' AND pid <> pg_backend_pid();
"
```

### Memory Issues
```bash
# Check memory usage
free -h
docker stats --no-stream

# Find memory-hungry processes
ps aux --sort=-%mem | head -10

# Clear system cache (Linux)
sudo sync && sudo sysctl vm.drop_caches=3
```

---

## 📞 When All Else Fails

1. **Check the logs first**: `docker-compose -f docker-compose.dev.yml logs -f`
2. **Restart the problematic service**: `docker-compose -f docker-compose.dev.yml restart [service]`
3. **Check environment variables**: Services might be misconfigured
4. **Verify external dependencies**: Database, Redis, RabbitMQ connections
5. **Nuclear option**: `docker-compose -f docker-compose.dev.yml down -v && docker-compose -f docker-compose.dev.yml up -d`

Remember: **Always check the service logs first!** 99% of issues are visible in the logs.
