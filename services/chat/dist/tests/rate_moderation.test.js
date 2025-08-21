"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const db_1 = __importDefault(require("../src/db"));
const moderation_1 = __importDefault(require("../src/moderation"));
const rate_limit_1 = __importDefault(require("../src/rate_limit"));
describe('rate limiting and moderation', () => {
    it('limits messages per user', () => {
        const limiter = new rate_limit_1.default(2, 1000);
        expect(limiter.attempt('u1')).toBe(true);
        expect(limiter.attempt('u1')).toBe(true);
        expect(limiter.attempt('u1')).toBe(false);
    });
    it('blocks users and detects profanity', () => {
        const mod = new moderation_1.default(['badguy']);
        expect(() => mod.checkMessage('badguy', 'hi')).toThrow('blocked');
        expect(() => mod.checkMessage('u1', 'this has badword in it')).toThrow('profanity');
        expect(() => mod.checkMessage('u1', 'clean message')).not.toThrow();
    });
    it('admin deletions are audited', () => {
        const db = new db_1.default();
        const mod = new moderation_1.default();
        const dialog = db.createDialog();
        const msg = db.appendMessage(dialog, 'u1', 'hi');
        mod.deleteMessageAsAdmin(db, msg.id, 'admin');
        const log = mod.auditLog[0];
        expect(log).toMatchObject({ adminId: 'admin', messageId: msg.id });
        const history = db.getMessages(dialog);
        expect(history.messages).toHaveLength(0);
    });
});
