"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
/* eslint-disable @typescript-eslint/no-explicit-any */
const db_1 = __importDefault(require("../src/db"));
const history_1 = require("../src/http/history");
function callHandler(handler, req) {
    return new Promise((resolve) => {
        const res = { json: (body) => resolve(body) };
        handler(req, res);
    });
}
describe('history endpoint', () => {
    it('paginates messages and skips deleted', async () => {
        const db = new db_1.default();
        const dialog = db.createDialog();
        const m1 = db.appendMessage(dialog, 'u1', 'hello');
        const m2 = db.appendMessage(dialog, 'u2', 'hi');
        const m3 = db.appendMessage(dialog, 'u1', 'third', [{ url: 'http://file', mimeType: 'text/plain' }]);
        db.softDeleteMessage(m2.id);
        const handler = (0, history_1.historyHandler)(db);
        const page1 = await callHandler(handler, { params: { dialogId: dialog }, query: { limit: '2' } });
        expect(page1.messages).toHaveLength(2);
        expect(page1.messages[0].id).toBe(m1.id);
        expect(page1.messages[1].id).toBe(m3.id);
        expect(page1.messages[1].attachments).toHaveLength(1);
        expect(page1.nextCursor).toBeNull();
    });
    it('supports cursor pagination', async () => {
        const db = new db_1.default();
        const dialog = db.createDialog();
        db.appendMessage(dialog, 'u1', 'm1');
        db.appendMessage(dialog, 'u1', 'm2');
        const m3 = db.appendMessage(dialog, 'u1', 'm3');
        const handler = (0, history_1.historyHandler)(db);
        const first = await callHandler(handler, { params: { dialogId: dialog }, query: { limit: '2' } });
        expect(first.messages).toHaveLength(2);
        const next = await callHandler(handler, {
            params: { dialogId: dialog },
            query: { limit: '2', cursor: first.nextCursor },
        });
        expect(next.messages).toHaveLength(1);
        expect(next.messages[0].id).toBe(m3.id);
    });
});
