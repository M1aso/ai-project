import http from 'http';
import express from 'express';
import WebSocket, { WebSocketServer } from 'ws';
import jwt from 'jsonwebtoken';
import { createRedisClient } from './redis';
import { PresenceService } from './presence';

interface Client {
  userId: string;
  ws: WebSocket;
  rooms: Set<string>;
}

const app = express();
app.use(express.json());

// OpenAPI specification for Chat Service
const openAPISpec = {
  openapi: '3.0.0',
  info: {
    title: 'AI Project - Chat Service',
    description: 'Real-time chat service with WebSocket support for messaging and presence',
    version: '1.0.0',
  },
  servers: [
    { url: 'http://api.45.146.164.70.nip.io', description: 'Development server' }
  ],
  paths: {
    '/api/chats/healthz': {
      get: {
        tags: ['Health'],
        summary: 'Health check',
        description: 'Check if the chat service is healthy',
        responses: {
          '200': {
            description: 'Service is healthy',
            content: {
              'text/plain': {
                example: 'OK'
              }
            }
          }
        }
      }
    },
    '/ws': {
      get: {
        tags: ['WebSocket'],
        summary: 'WebSocket connection',
        description: 'Establish WebSocket connection for real-time chat',
        parameters: [
          {
            name: 'token',
            in: 'query',
            description: 'JWT authentication token',
            required: true,
            schema: { type: 'string' }
          },
          {
            name: 'roomId',
            in: 'query',
            description: 'Chat room ID to join',
            required: false,
            schema: { type: 'string', default: 'lobby' }
          }
        ],
        responses: {
          '101': { description: 'Switching Protocols - WebSocket connection established' },
          '401': { description: 'Unauthorized - Invalid JWT token' }
        }
      }
    }
  },
  tags: [
    { name: 'Health', description: 'Health check operations' },
    { name: 'WebSocket', description: 'Real-time WebSocket operations' },
    { name: 'Chat', description: 'Chat messaging operations' },
    { name: 'Presence', description: 'User presence and status' }
  ]
};

app.get('/healthz', (_req, res) => res.send('OK'));

// OpenAPI endpoints
app.get('/api/chats/openapi.json', (_req, res) => {
  res.json(openAPISpec);
});

app.get('/api/chats/docs', (_req, res) => {
  const html = `<!DOCTYPE html>
<html>
<head>
    <title>Chat Service - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '/api/chats/openapi.json',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ]
        });
    </script>
</body>
</html>`;
  res.send(html);
});

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

const redis = createRedisClient();
const presence = new PresenceService(redis);
const clients = new Map<WebSocket, Client>();
const rooms = new Map<string, Set<Client>>();

presence.onPresence((userId, status) => {
  const payload = JSON.stringify({ type: 'presence', userId, status });
  for (const members of rooms.values()) {
    members.forEach((client) => {
      if (client.userId !== userId) client.ws.send(payload);
    });
  }
});

wss.on('connection', (ws, req) => {
  const url = new URL(req.url || '', 'http://localhost');
  const token = url.searchParams.get('token') || req.headers['authorization']?.split(' ')[1];
  const roomId = url.searchParams.get('roomId') || 'lobby';

  let userId: string;
  try {
    const payload = jwt.verify(token || '', process.env.JWT_SECRET || 'secret') as { sub: string };
    userId = payload.sub;
  } catch {
    ws.close();
    return;
  }

  const client: Client = { userId, ws, rooms: new Set([roomId]) };
  clients.set(ws, client);

  if (!rooms.has(roomId)) rooms.set(roomId, new Set());
  rooms.get(roomId)!.add(client);

  presence.setOnline(userId).catch(() => undefined);

  ws.on('close', () => {
    clients.delete(ws);
    rooms.get(roomId)?.delete(client);
    presence.setOffline(userId).catch(() => undefined);
  });
});

const PORT = Number(process.env.PORT) || 8000;
server.listen(PORT, () => {
  console.log(`chat service listening on ${PORT}`);
});
