import Redis, { Redis as RedisClient } from 'ioredis';

export function createRedisClient(): RedisClient {
  const url = process.env.REDIS_URL || 'redis://localhost:6379';
  return new Redis(url);
}
