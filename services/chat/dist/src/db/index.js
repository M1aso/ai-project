"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatDB = void 0;
const crypto_1 = require("crypto");
class ChatDB {
    constructor() {
        this.dialogs = new Set();
        this.messages = new Map();
        this.byDialog = new Map();
    }
    createDialog(id) {
        const dialogId = id || (0, crypto_1.randomUUID)();
        this.dialogs.add(dialogId);
        if (!this.byDialog.has(dialogId))
            this.byDialog.set(dialogId, []);
        return dialogId;
    }
    appendMessage(dialogId, senderId, content, attachments = []) {
        if (!this.dialogs.has(dialogId))
            this.createDialog(dialogId);
        const msg = {
            id: (0, crypto_1.randomUUID)(),
            dialogId,
            senderId,
            content,
            createdAt: new Date(),
            deletedAt: null,
            attachments: attachments.map((a) => ({
                id: (0, crypto_1.randomUUID)(),
                url: a.url,
                mimeType: a.mimeType,
                sizeBytes: a.sizeBytes,
                createdAt: new Date(),
            })),
        };
        this.messages.set(msg.id, msg);
        this.byDialog.get(dialogId).push(msg);
        return msg;
    }
    softDeleteMessage(id) {
        const msg = this.messages.get(id);
        if (msg && !msg.deletedAt) {
            msg.deletedAt = new Date();
        }
    }
    getMessages(dialogId, limit = 20, cursor) {
        const all = this.byDialog.get(dialogId) || [];
        const visible = all.filter((m) => !m.deletedAt);
        visible.sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime());
        let start = 0;
        if (cursor) {
            const idx = visible.findIndex((m) => m.id === cursor);
            if (idx !== -1)
                start = idx + 1;
        }
        const slice = visible.slice(start, start + limit);
        const nextCursor = start + slice.length < visible.length ? slice[slice.length - 1].id : null;
        return { messages: slice, nextCursor };
    }
    presignAttachment(filename) {
        const id = (0, crypto_1.randomUUID)();
        return `https://minio.local/${id}/${encodeURIComponent(filename)}`;
    }
}
exports.ChatDB = ChatDB;
exports.default = ChatDB;
