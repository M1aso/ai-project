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
app.get('/healthz', (_req, res) => res.send('OK'));

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
