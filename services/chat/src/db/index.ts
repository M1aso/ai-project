import { randomUUID } from 'crypto';

export interface Attachment {
  id: string;
  url: string;
  mimeType?: string;
  sizeBytes?: number;
  createdAt: Date;
}

export interface Message {
  id: string;
  dialogId: string;
  senderId: string;
  content: string;
  createdAt: Date;
  deletedAt: Date | null;
  attachments: Attachment[];
}

export class ChatDB {
  private dialogs = new Set<string>();
  private messages = new Map<string, Message>();
  private byDialog = new Map<string, Message[]>();

  createDialog(id?: string): string {
    const dialogId = id || randomUUID();
    this.dialogs.add(dialogId);
    if (!this.byDialog.has(dialogId)) this.byDialog.set(dialogId, []);
    return dialogId;
  }

  appendMessage(
    dialogId: string,
    senderId: string,
    content: string,
    attachments: Array<{
      url: string;
      mimeType?: string;
      sizeBytes?: number;
    }> = []
  ): Message {
    if (!this.dialogs.has(dialogId)) this.createDialog(dialogId);
    const msg: Message = {
      id: randomUUID(),
      dialogId,
      senderId,
      content,
      createdAt: new Date(),
      deletedAt: null,
      attachments: attachments.map((a) => ({
        id: randomUUID(),
        url: a.url,
        mimeType: a.mimeType,
        sizeBytes: a.sizeBytes,
        createdAt: new Date(),
      })),
    };
    this.messages.set(msg.id, msg);
    this.byDialog.get(dialogId)!.push(msg);
    return msg;
  }

  softDeleteMessage(id: string): void {
    const msg = this.messages.get(id);
    if (msg && !msg.deletedAt) {
      msg.deletedAt = new Date();
    }
  }

  getMessages(
    dialogId: string,
    limit = 20,
    cursor?: string
  ): { messages: Message[]; nextCursor: string | null } {
    const all = this.byDialog.get(dialogId) || [];
    const visible = all.filter((m) => !m.deletedAt);
    visible.sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime());
    let start = 0;
    if (cursor) {
      const idx = visible.findIndex((m) => m.id === cursor);
      if (idx !== -1) start = idx + 1;
    }
    const slice = visible.slice(start, start + limit);
    const nextCursor = start + slice.length < visible.length ? slice[slice.length - 1].id : null;
    return { messages: slice, nextCursor };
  }

  presignAttachment(filename: string): string {
    const id = randomUUID();
    return `https://minio.local/${id}/${encodeURIComponent(filename)}`;
  }
}

export default ChatDB;
