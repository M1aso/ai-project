import { Redis as RedisClient } from 'ioredis';

export type PresenceHandler = (userId: string, status: 'online' | 'offline') => void;

export class PresenceService {
  private redis: RedisClient;
  private pub: RedisClient;
  private sub: RedisClient;
  private channel = 'presence';

  constructor(redis: RedisClient) {
    this.redis = redis;
    this.pub = redis;
    this.sub = redis.duplicate();
  }

  async setOnline(userId: string, ttl = 30): Promise<void> {
    await this.redis.set(`online:${userId}`, '1', 'EX', ttl);
    await this.pub.publish(this.channel, JSON.stringify({ userId, status: 'online' }));
  }

  async setOffline(userId: string): Promise<void> {
    await this.redis.del(`online:${userId}`);
    await this.pub.publish(this.channel, JSON.stringify({ userId, status: 'offline' }));
  }

  async isOnline(userId: string): Promise<boolean> {
    return (await this.redis.exists(`online:${userId}`)) === 1;
  }

  onPresence(handler: PresenceHandler): void {
    this.sub.subscribe(this.channel);
    this.sub.on('message', (_: string, message: string) => {
      const { userId, status } = JSON.parse(message) as { userId: string; status: 'online' | 'offline' };
      handler(userId, status);
    });
  }
}
