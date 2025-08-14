import ChatDB from '../src/db';
import ModerationService from '../src/moderation';
import RateLimiter from '../src/rate_limit';

describe('rate limiting and moderation', () => {
  it('limits messages per user', () => {
    const limiter = new RateLimiter(2, 1000);
    expect(limiter.attempt('u1')).toBe(true);
    expect(limiter.attempt('u1')).toBe(true);
    expect(limiter.attempt('u1')).toBe(false);
  });

  it('blocks users and detects profanity', () => {
    const mod = new ModerationService(['badguy']);
    expect(() => mod.checkMessage('badguy', 'hi')).toThrow('blocked');
    expect(() => mod.checkMessage('u1', 'this has badword in it')).toThrow('profanity');
    expect(() => mod.checkMessage('u1', 'clean message')).not.toThrow();
  });

  it('admin deletions are audited', () => {
    const db = new ChatDB();
    const mod = new ModerationService();
    const dialog = db.createDialog();
    const msg = db.appendMessage(dialog, 'u1', 'hi');
    mod.deleteMessageAsAdmin(db, msg.id, 'admin');
    const log = mod.auditLog[0];
    expect(log).toMatchObject({ adminId: 'admin', messageId: msg.id });
    const history = db.getMessages(dialog);
    expect(history.messages).toHaveLength(0);
  });
});
