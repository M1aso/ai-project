"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ModerationService = void 0;
class ModerationService {
    constructor(blocked = [], filters = []) {
        this.auditLog = [];
        this.blocklist = new Set(blocked);
        const profanity = (text) => {
            const bad = ['badword'];
            const lower = text.toLowerCase();
            return !bad.some((w) => lower.includes(w));
        };
        this.filters = [profanity, ...filters];
    }
    isBlocked(userId) {
        return this.blocklist.has(userId);
    }
    checkMessage(userId, text) {
        if (this.isBlocked(userId))
            throw new Error('blocked');
        if (!this.filters.every((f) => f(text)))
            throw new Error('profanity');
    }
    deleteMessageAsAdmin(db, messageId, adminId) {
        db.softDeleteMessage(messageId);
        this.auditLog.push({ adminId, messageId, deletedAt: new Date() });
    }
}
exports.ModerationService = ModerationService;
exports.default = ModerationService;
