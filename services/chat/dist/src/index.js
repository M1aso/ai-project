"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const http_1 = __importDefault(require("http"));
const express_1 = __importDefault(require("express"));
const ws_1 = require("ws");
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const redis_1 = require("./redis");
const presence_1 = require("./presence");
const app = (0, express_1.default)();
app.get('/healthz', (_req, res) => res.send('OK'));
const server = http_1.default.createServer(app);
const wss = new ws_1.WebSocketServer({ server, path: '/ws' });
const redis = (0, redis_1.createRedisClient)();
const presence = new presence_1.PresenceService(redis);
const clients = new Map();
const rooms = new Map();
presence.onPresence((userId, status) => {
    const payload = JSON.stringify({ type: 'presence', userId, status });
    for (const members of rooms.values()) {
        members.forEach((client) => {
            if (client.userId !== userId)
                client.ws.send(payload);
        });
    }
});
wss.on('connection', (ws, req) => {
    const url = new URL(req.url || '', 'http://localhost');
    const token = url.searchParams.get('token') || req.headers['authorization']?.split(' ')[1];
    const roomId = url.searchParams.get('roomId') || 'lobby';
    let userId;
    try {
        const payload = jsonwebtoken_1.default.verify(token || '', process.env.JWT_SECRET || 'secret');
        userId = payload.sub;
    }
    catch {
        ws.close();
        return;
    }
    const client = { userId, ws, rooms: new Set([roomId]) };
    clients.set(ws, client);
    if (!rooms.has(roomId))
        rooms.set(roomId, new Set());
    rooms.get(roomId).add(client);
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
