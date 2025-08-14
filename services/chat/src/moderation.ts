import type ChatDB from './db';

export type Filter = (text: string) => boolean;

export interface AuditEntry {
  adminId: string;
  messageId: string;
  deletedAt: Date;
}

export class ModerationService {
  private blocklist: Set<string>;
  private filters: Filter[];
  public auditLog: AuditEntry[] = [];

  constructor(blocked: string[] = [], filters: Filter[] = []) {
    this.blocklist = new Set(blocked);
    const profanity = (text: string) => {
      const bad = ['badword'];
      const lower = text.toLowerCase();
      return !bad.some((w) => lower.includes(w));
    };
    this.filters = [profanity, ...filters];
  }

  isBlocked(userId: string): boolean {
    return this.blocklist.has(userId);
  }

  checkMessage(userId: string, text: string): void {
    if (this.isBlocked(userId)) throw new Error('blocked');
    if (!this.filters.every((f) => f(text))) throw new Error('profanity');
  }

  deleteMessageAsAdmin(db: ChatDB, messageId: string, adminId: string): void {
    db.softDeleteMessage(messageId);
    this.auditLog.push({ adminId, messageId, deletedAt: new Date() });
  }
}

export default ModerationService;
