import { createClient } from 'redis';

const redis = createClient({
  url: process.env.REDIS_URL,
});

redis.on('error', err => console.log('Redis Client Error', err));

async function connect() {
  if (!redis.isOpen) {
    await redis.connect();
  }
}

connect();

export default redis;
