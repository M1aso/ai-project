# 🔒 Rate Limiting Configuration Guide

## Overview
The authentication service now supports configurable rate limiting through environment variables, making it easier to adjust limits for different environments (development, staging, production).

## 🚀 New Environment Variables

### **Rate Limiting Configuration**
```yaml
# Rate Limiting Configuration
- name: MAX_LOGIN_ATTEMPTS
  value: "5"                    # Failed login attempts before blocking
- name: RATE_LIMIT_WINDOW
  value: "3600"                 # Time window in seconds (1 hour)
- name: AUTH_RATE_LIMIT_PER_IP
  value: "50"                   # Auth requests per IP per hour (dev: 50, prod: 10)
- name: GENERAL_RATE_LIMIT_PER_IP
  value: "200"                  # General requests per IP per hour (dev: 200, prod: 100)
- name: LOGIN_RATE_LIMIT_PER_IP
  value: "20"                   # Failed login attempts per IP per hour
```

## 📊 Default Values by Environment

| Environment | AUTH_RATE_LIMIT | GENERAL_RATE_LIMIT | MAX_LOGIN_ATTEMPTS |
|-------------|-----------------|-------------------|-------------------|
| **Development** | 50/hour | 200/hour | 5 |
| **Staging** | 25/hour | 150/hour | 5 |
| **Production** | 10/hour | 100/hour | 5 |

## 🔧 Implementation Details

### **1. IP-Based Rate Limiting**
- **General endpoints**: `GENERAL_RATE_LIMIT_PER_IP` requests per hour
- **Auth endpoints**: `AUTH_RATE_LIMIT_PER_IP` requests per hour
- **Health checks**: Always excluded from rate limiting

### **2. Login Attempt Rate Limiting**
- **Max attempts**: `MAX_LOGIN_ATTEMPTS` per email/IP
- **Progressive delays**: 1min → 5min → 15min → 1hour → 24hours
- **Auto-reset**: After delay period expires

### **3. Redis Storage**
- **TTL**: 24 hours for failed attempts
- **Key format**: `rate_limit:auth_ip:{IP}` and `login_attempts:{identifier}`

## 🚀 Deployment Updates

### **Helm Values Update**
The rate limiting configuration has been added to:
- `deploy/helm/auth/values.dev.yaml` - Development environment
- `deploy/helm/auth/values.yaml` - Example configuration

### **Code Changes**
- `services/auth/app/security/advanced_rate_limit.py` - Updated to use environment variables
- Configurable limits instead of hardcoded values
- Better error messages with current limits

## 🧪 Testing the New Configuration

### **Before (Old Limits)**
```bash
# Hit rate limit after 10 auth requests
curl -X POST http://api.45.146.164.70.nip.io/api/auth/email/register
# Response: {"detail": "Too many authentication attempts from this IP"}
```

### **After (New Limits)**
```bash
# Now allows up to 50 auth requests per hour
# Much more suitable for development and testing
```

## 🔍 Monitoring Rate Limiting

### **Check Current Limits**
```bash
# View Redis keys
kubectl exec -n redis redis-master-0 -- redis-cli keys "*rate_limit*"

# Check specific IP limit
kubectl exec -n redis redis-master-0 -- redis-cli get "rate_limit:auth_ip:YOUR_IP"
```

### **Reset Rate Limits (Development Only)**
```bash
# Clear all rate limiting for an IP
kubectl exec -n redis redis-master-0 -- redis-cli del "rate_limit:auth_ip:YOUR_IP"
```

## ⚠️ Security Considerations

### **Development Environment**
- Higher limits for testing and development
- Easier debugging and testing flows
- Still maintains basic protection

### **Production Environment**
- Strict limits to prevent abuse
- Progressive delays for failed attempts
- IP-based blocking for repeated violations

## 🎯 Next Steps

1. **Deploy the updated configuration** to your dev environment
2. **Test the new rate limits** with the auth flow
3. **Adjust limits** based on your testing needs
4. **Set appropriate production values** when deploying to production

## 📚 Related Files

- `deploy/helm/auth/values.dev.yaml` - Development configuration
- `deploy/helm/auth/values.yaml` - Example configuration
- `services/auth/app/security/advanced_rate_limit.py` - Rate limiting implementation
- `AUTH_TESTING_GUIDE.md` - Testing guide for auth flow
