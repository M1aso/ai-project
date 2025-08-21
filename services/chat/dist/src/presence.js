"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PresenceService = void 0;
class PresenceService {
    constructor(redis) {
        this.channel = 'presence';
        this.redis = redis;
        this.pub = redis;
        this.sub = redis.duplicate();
    }
    async setOnline(userId, ttl = 30) {
        await this.redis.set(`online:${userId}`, '1', 'EX', ttl);
        await this.pub.publish(this.channel, JSON.stringify({ userId, status: 'online' }));
    }
    async setOffline(userId) {
        await this.redis.del(`online:${userId}`);
        await this.pub.publish(this.channel, JSON.stringify({ userId, status: 'offline' }));
    }
    async isOnline(userId) {
        return (await this.redis.exists(`online:${userId}`)) === 1;
    }
    onPresence(handler) {
        this.sub.subscribe(this.channel);
        this.sub.on('message', (_, message) => {
            const { userId, status } = JSON.parse(message);
            handler(userId, status);
        });
    }
}
exports.PresenceService = PresenceService;
