"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-ignore
const ioredis_mock_1 = __importDefault(require("ioredis-mock"));
const presence_1 = require("../src/presence");
describe('PresenceService', () => {
    it('tracks online users with TTL', async () => {
        const redis = new ioredis_mock_1.default();
        const presence = new presence_1.PresenceService(redis);
        const helper = redis;
        await presence.setOnline('u1', 5);
        const ttl = await helper.ttl('online:u1');
        expect(ttl).toBeGreaterThan(0);
        await presence.setOffline('u1');
        const exists = await helper.exists('online:u1');
        expect(exists).toBe(0);
    });
    it('propagates presence via pubsub', async () => {
        const redis = new ioredis_mock_1.default();
        const serviceA = new presence_1.PresenceService(redis);
        const serviceB = new presence_1.PresenceService(redis.duplicate());
        const started = Date.now();
        const received = new Promise((resolve) => {
            serviceB.onPresence((userId, status) => resolve({ userId, status }));
        });
        await serviceA.setOnline('u42', 5);
        const msg = await received;
        const elapsed = Date.now() - started;
        expect(msg).toEqual({ userId: 'u42', status: 'online' });
        expect(elapsed).toBeLessThan(1000);
    });
});
