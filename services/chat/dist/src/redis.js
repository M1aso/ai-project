"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createRedisClient = createRedisClient;
const ioredis_1 = __importDefault(require("ioredis"));
function createRedisClient() {
    const url = process.env.REDIS_URL || 'redis://localhost:6379';
    return new ioredis_1.default(url);
}
