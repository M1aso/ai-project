import Redis, { Redis as RedisType } from 'ioredis';

export function createRedisClient(): RedisType {
  const url = process.env.REDIS_URL || 'redis://localhost:6379';
  return new Redis(url);
}
