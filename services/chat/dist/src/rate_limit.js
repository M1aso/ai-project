"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RateLimiter = void 0;
class RateLimiter {
    constructor(limit = 20, windowMs = 10000) {
        this.hits = new Map();
        this.limit = limit;
        this.windowMs = windowMs;
    }
    attempt(userId) {
        const now = Date.now();
        const arr = this.hits.get(userId) || [];
        const fresh = arr.filter((ts) => now - ts < this.windowMs);
        fresh.push(now);
        this.hits.set(userId, fresh);
        return fresh.length <= this.limit;
    }
}
exports.RateLimiter = RateLimiter;
exports.default = RateLimiter;
