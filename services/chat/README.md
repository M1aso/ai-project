# Chat Service

## Overview
The Chat Service is a Node.js/TypeScript-based real-time messaging service that provides WebSocket connections for instant messaging, presence tracking, and room-based chat functionality.

## Features
- 💬 **Real-time Messaging** - WebSocket-based instant messaging
- 🏠 **Room-based Chat** - Support for multiple chat rooms
- 👥 **Presence Tracking** - Online/offline status with Redis persistence
- 🔒 **JWT Authentication** - Secure WebSocket connections with token validation
- 🛡️ **Message Moderation** - Built-in content moderation and audit logging
- ⚡ **Rate Limiting** - Protection against message spam
- 📊 **Chat History** - Persistent message storage and retrieval

## Technology Stack
- **Runtime**: Node.js 20
- **Language**: TypeScript
- **Framework**: Express.js + WebSocket (ws library)
- **Authentication**: JWT token validation
- **Cache/Presence**: Redis with ioredis client
- **Real-time**: Native WebSocket connections
- **Moderation**: Built-in message filtering and audit system

## Architecture
```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Web Client    │◄──►│   Chat       │◄──►│     Redis       │
│  (WebSocket)    │    │   Service    │    │  (Presence)     │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   Database   │
                       │  (History)   │
                       └──────────────┘
```

## API Endpoints

### HTTP Endpoints
- `GET /healthz` - Health check
- `GET /api/chats/openapi.json` - OpenAPI specification
- `GET /api/chats/docs` - Swagger UI documentation

### WebSocket Endpoint
- `WS /ws` - WebSocket connection for real-time chat

## WebSocket Connection

### Authentication
WebSocket connections require JWT authentication via query parameter or header:

```javascript
// Via query parameter
const ws = new WebSocket('ws://api.example.com/ws?token=<jwt-token>&roomId=general');

// Via Authorization header
const ws = new WebSocket('ws://api.example.com/ws?roomId=general', {
  headers: {
    'Authorization': 'Bearer <jwt-token>'
  }
});
```

### Connection Parameters
- `token` (required) - JWT authentication token
- `roomId` (optional) - Chat room to join (default: "lobby")

## Message Protocol

### Client → Server Messages
```json
{
  "type": "message",
  "roomId": "general",
  "content": "Hello everyone!",
  "timestamp": "2024-01-01T12:00:00Z"
}

{
  "type": "join_room",
  "roomId": "development"
}

{
  "type": "leave_room", 
  "roomId": "general"
}

{
  "type": "typing",
  "roomId": "general",
  "isTyping": true
}
```

### Server → Client Messages
```json
{
  "type": "message",
  "messageId": "msg-123",
  "userId": "user-456",
  "username": "john_doe",
  "roomId": "general",
  "content": "Hello everyone!",
  "timestamp": "2024-01-01T12:00:00Z"
}

{
  "type": "presence",
  "userId": "user-456",
  "status": "online"
}

{
  "type": "room_joined",
  "roomId": "development",
  "memberCount": 5
}

{
  "type": "typing_indicator",
  "userId": "user-789",
  "roomId": "general",
  "isTyping": true
}
```

## Environment Variables
```bash
# Server Configuration
PORT=8000
NODE_ENV=development

# Authentication
JWT_SECRET=your-jwt-secret-key

# Redis (for presence and caching)
REDIS_URL=redis://redis:6379

# Database (for message history)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000  # 1 minute
RATE_LIMIT_MAX_MESSAGES=30  # 30 messages per minute

# Moderation
ENABLE_MODERATION=true
MAX_MESSAGE_LENGTH=1000
```

## Features

### Presence Tracking
```typescript
class PresenceService {
  async setOnline(userId: string): Promise<void>
  async setOffline(userId: string): Promise<void>
  async getOnlineUsers(roomId?: string): Promise<string[]>
  async getUserStatus(userId: string): Promise<'online' | 'offline'>
}
```

### Message Moderation
```typescript
class ModerationService {
  filterMessage(content: string): string
  isMessageAllowed(content: string): boolean
  auditMessage(messageId: string, userId: string, action: string): void
}
```

### Rate Limiting
```typescript
class RateLimiter {
  isAllowed(userId: string): boolean
  recordMessage(userId: string): void
  getRemainingQuota(userId: string): number
}
```

## Client Integration

### JavaScript/Browser
```javascript
class ChatClient {
  constructor(token, roomId = 'lobby') {
    this.ws = new WebSocket(`ws://api.example.com/ws?token=${token}&roomId=${roomId}`);
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    this.ws.onopen = () => console.log('Connected to chat');
    this.ws.onmessage = (event) => this.handleMessage(JSON.parse(event.data));
    this.ws.onclose = () => console.log('Disconnected from chat');
    this.ws.onerror = (error) => console.error('Chat error:', error);
  }

  sendMessage(content, roomId) {
    this.ws.send(JSON.stringify({
      type: 'message',
      content,
      roomId,
      timestamp: new Date().toISOString()
    }));
  }

  joinRoom(roomId) {
    this.ws.send(JSON.stringify({
      type: 'join_room',
      roomId
    }));
  }
}

// Usage
const chat = new ChatClient('your-jwt-token', 'general');
chat.sendMessage('Hello world!', 'general');
```

### React Hook
```typescript
import { useState, useEffect, useRef } from 'react';

export function useChat(token: string, roomId: string = 'lobby') {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket(`ws://api.example.com/ws?token=${token}&roomId=${roomId}`);
    
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);
    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'message') {
        setMessages(prev => [...prev, message]);
      }
    };

    return () => ws.current?.close();
  }, [token, roomId]);

  const sendMessage = (content: string) => {
    if (ws.current && isConnected) {
      ws.current.send(JSON.stringify({
        type: 'message',
        content,
        roomId,
        timestamp: new Date().toISOString()
      }));
    }
  };

  return { messages, isConnected, sendMessage };
}
```

## Development

### Prerequisites
- Node.js 20+
- Redis server
- PostgreSQL database (for message history)

### Setup
```bash
# Install dependencies
npm install

# Build TypeScript
npm run build

# Start development server
npm run dev

# Run tests
npm test

# Start with watch mode
npm run start:dev
```

### Testing
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run WebSocket integration tests
npm run test:integration

# Test with multiple clients
npm run test:load
```

## Deployment
The service is deployed using Docker and Helm in Kubernetes:
- **Docker Image**: Built from Node.js 20 Alpine
- **Health Checks**: `/healthz` endpoint
- **Scaling**: Horizontal pod autoscaling based on connection count
- **Session Affinity**: Sticky sessions for WebSocket connections
- **Monitoring**: Built-in metrics and logging

## Security Features
- 🔒 **JWT Authentication** - All WebSocket connections require valid tokens
- ⚡ **Rate Limiting** - Protection against message spam and DoS
- 🛡️ **Message Moderation** - Content filtering and audit logging  
- 🔐 **Connection Security** - Invalid tokens cause immediate disconnect
- 📊 **Audit Trail** - Complete message and action logging
- 🚫 **Input Validation** - Message content and length validation

## Monitoring & Observability

### Metrics
- **Connection Count**: Active WebSocket connections
- **Message Rate**: Messages per second by room
- **Presence Updates**: Online/offline status changes
- **Error Rate**: Connection failures and message errors
- **Latency**: Message delivery time

### Logging
```typescript
// Structured logging for operations
logger.info('WebSocket connection established', {
  userId,
  roomId,
  userAgent: req.headers['user-agent']
});

logger.warn('Rate limit exceeded', {
  userId,
  messageCount: rateLimiter.getCount(userId),
  timeWindow: '1m'
});
```

## Performance Considerations

### Scaling
- **Horizontal Scaling**: Multiple chat service instances
- **Redis Clustering**: Distributed presence and caching
- **Load Balancing**: WebSocket-aware load balancing
- **Connection Pooling**: Efficient database connections

### Optimization
- **Message Batching**: Batch presence updates
- **Connection Cleanup**: Automatic cleanup of stale connections
- **Memory Management**: Efficient message queuing
- **Compression**: WebSocket message compression

## Documentation
- **OpenAPI Spec**: `/api/chats/openapi.json`
- **Swagger UI**: `/api/chats/docs`
- **WebSocket Events**: Documented message protocol
- **Client Examples**: Integration examples for different platforms