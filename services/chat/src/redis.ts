import Redis from 'ioredis';

export type RedisClient = InstanceType<typeof Redis>;

export function createRedisClient(): RedisClient {
  const url = process.env.REDIS_URL || 'redis://localhost:6379';
  return new Redis(url);
}
