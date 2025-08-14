/* eslint-disable @typescript-eslint/ban-ts-comment */
// @ts-ignore
import Redis from 'ioredis-mock';
/* eslint-enable @typescript-eslint/ban-ts-comment */
import type { Redis as RedisClient } from 'ioredis';
import { PresenceService } from '../src/presence';

describe('PresenceService', () => {
  it('tracks online users with TTL', async () => {
    const redis = new Redis() as unknown as RedisClient;
    const presence = new PresenceService(redis);
    const helper = redis as unknown as {
      ttl: (key: string) => Promise<number>;
      exists: (key: string) => Promise<number>;
    };
    await presence.setOnline('u1', 5);
    const ttl = await helper.ttl('online:u1');
    expect(ttl).toBeGreaterThan(0);
    await presence.setOffline('u1');
    const exists = await helper.exists('online:u1');
    expect(exists).toBe(0);
  });

  it('propagates presence via pubsub', async () => {
    const redis = new Redis() as unknown as RedisClient;
    const serviceA = new PresenceService(redis);
    const serviceB = new PresenceService((redis.duplicate() as unknown) as RedisClient);
    const started = Date.now();
    const received = new Promise<{ userId: string; status: string }>((resolve) => {
      serviceB.onPresence((userId, status) => resolve({ userId, status }));
    });
    await serviceA.setOnline('u42', 5);
    const msg = await received;
    const elapsed = Date.now() - started;
    expect(msg).toEqual({ userId: 'u42', status: 'online' });
    expect(elapsed).toBeLessThan(1000);
  });
});
