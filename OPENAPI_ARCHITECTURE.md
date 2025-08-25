# 🚀 Dynamic OpenAPI Architecture

## Overview

This document describes the new **dynamic OpenAPI architecture** that eliminates static YAML files and provides always-up-to-date API documentation.

## 🏗️ Architecture Components

### 1. **Service-Level OpenAPI Generation**
Each service generates its OpenAPI specification dynamically:

- **🔐 Auth Service**: FastAPI with comprehensive OpenAPI metadata
- **👤 Profile Service**: FastAPI with professional documentation
- **📊 Analytics Service**: FastAPI with detailed endpoint categorization
- **📢 Notifications Service**: FastAPI with clear service descriptions
- **📁 Content Service**: Go service with manual OpenAPI spec
- **💬 Chat Service**: Node.js service with manual OpenAPI spec

### 2. **API Gateway Integration**
All services expose OpenAPI endpoints at `/api/{service}/openapi.json` for compatibility with the API Gateway's prefix rewriting.

### 3. **Centralized Swagger UI**
Single Swagger UI instance at [http://docs.45.146.164.70.nip.io](http://docs.45.146.164.70.nip.io) that fetches live specs from all services.

## 🔄 CI/CD Pipeline

### **Before (Static Files)**
```yaml
contracts_lint:
  - run: npx spectral lint "libs/contracts/*.yaml"
```

### **After (Live Specs)**
```yaml
contracts_lint:
  - Start services in CI environment
  - Generate live OpenAPI specs
  - Lint live specs with Spectral
  - Validate actual API behavior
```

## 📁 File Structure Changes

### **Removed (No Longer Needed)**
```
libs/contracts/
├── auth.yaml          ❌ Deleted
├── profile.yaml       ❌ Deleted
├── content.yaml       ❌ Deleted
├── notifications.yaml ❌ Deleted
├── chat.yaml          ❌ Deleted
└── analytics.yaml     ❌ Deleted
```

### **Kept (Still Needed)**
```
libs/contracts/
└── .spectral.yaml     ✅ OpenAPI validation rules
```

## 🎯 Benefits

### **1. Zero Maintenance**
- No more manual YAML updates
- No more sync processes
- Documentation automatically matches code

### **2. Always Accurate**
- Live specs from running services
- Real-time validation of API behavior
- Catches actual implementation issues

### **3. Professional Quality**
- Comprehensive endpoint categorization
- Detailed request/response examples
- Interactive testing capabilities
- Proper security scheme documentation

### **4. Developer Experience**
- Single source of truth (the code)
- Automatic documentation updates
- Consistent API documentation across services
- Better onboarding for new developers

## 🔧 Implementation Details

### **FastAPI Services**
```python
@app.get("/api/{service}/openapi.json")
def get_openapi():
    """Custom OpenAPI endpoint for API gateway compatibility."""
    return app.openapi()

@app.get("/api/{service}/docs")
def get_docs():
    """Custom docs endpoint with proper OpenAPI URL."""
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(
        openapi_url=f"/api/{service}/openapi.json",
        title=app.title + " - Swagger UI",
    )
```

### **Go Service (Content)**
```go
// Manual OpenAPI specification
var openAPISpec = map[string]interface{}{
    "openapi": "3.0.0",
    "info": map[string]interface{}{
        "title": "AI Project - Content Service",
        "description": "Content management service",
        "version": "1.0.0",
    },
    // ... detailed spec
}

// Custom endpoints
r.Get("/api/content/openapi.json", func(w http.ResponseWriter, r *http.Request) {
    json.NewEncoder(w).Encode(openAPISpec)
})
```

### **Node.js Service (Chat)**
```typescript
// Manual OpenAPI specification
const openAPISpec = {
  openapi: '3.0.0',
  info: {
    title: 'AI Project - Chat Service',
    description: 'Real-time chat service with WebSocket support',
    version: '1.0.0',
  },
  // ... detailed spec
}

// Custom endpoints
app.get('/api/chats/openapi.json', (_req, res) => {
  res.json(openAPISpec)
})
```

## 🚀 Deployment

### **Swagger UI Configuration**
```yaml
swaggerConfig:
  urls:
    - url: "http://api.45.146.164.70.nip.io/api/auth/openapi.json"
      name: "🔐 Auth Service"
    - url: "http://api.45.146.164.70.nip.io/api/profile/openapi.json"
      name: "👤 Profile Service"
    # ... all other services
```

### **Service Deployment**
Each service automatically exposes its OpenAPI spec at `/api/{service}/openapi.json` when deployed.

## 🧪 Testing

### **Local Testing**
```bash
# Test individual service OpenAPI endpoints
curl http://localhost:8000/api/auth/openapi.json
curl http://localhost:8000/api/profile/openapi.json

# Test centralized Swagger UI
# Visit http://docs.45.146.164.70.nip.io
```

### **CI Testing**
The CI pipeline now:
1. Starts all services in test environment
2. Generates live OpenAPI specs
3. Validates specs with Spectral
4. Ensures API documentation quality

## 🔮 Future Enhancements

### **Potential Improvements**
- **OpenAPI 3.1 Support**: Upgrade to latest OpenAPI version
- **Schema Validation**: Add runtime schema validation
- **API Versioning**: Implement proper API versioning
- **Documentation Generation**: Auto-generate markdown docs from OpenAPI specs

### **Monitoring & Analytics**
- Track API documentation usage
- Monitor OpenAPI spec generation performance
- Alert on documentation inconsistencies

## 📚 Related Documentation

- **[API Documentation Guide](API_DOCUMENTATION.md)**: Detailed API documentation
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Complete development workflow
- **[Deployment Guide](DEPLOYMENT.md)**: Production deployment instructions
- **[Quick Start](QUICK_START.md)**: Get started in 15 minutes

---

*This architecture represents a significant improvement in API documentation quality, maintainability, and developer experience.*
