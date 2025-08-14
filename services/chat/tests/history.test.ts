/* eslint-disable @typescript-eslint/no-explicit-any */
import ChatDB from '../src/db';
import { historyHandler } from '../src/http/history';

function callHandler(handler: any, req: any) {
  return new Promise((resolve) => {
    const res = { json: (body: unknown) => resolve(body) };
    handler(req, res);
  });
}

describe('history endpoint', () => {
  it('paginates messages and skips deleted', async () => {
    const db = new ChatDB();
    const dialog = db.createDialog();
    const m1 = db.appendMessage(dialog, 'u1', 'hello');
    const m2 = db.appendMessage(dialog, 'u2', 'hi');
    const m3 = db.appendMessage(dialog, 'u1', 'third', [{ url: 'http://file', mimeType: 'text/plain' }]);
    db.softDeleteMessage(m2.id);

    const handler = historyHandler(db);
    const page1: any = await callHandler(handler, { params: { dialogId: dialog }, query: { limit: '2' } });
    expect(page1.messages).toHaveLength(2);
    expect(page1.messages[0].id).toBe(m1.id);
    expect(page1.messages[1].id).toBe(m3.id);
    expect(page1.messages[1].attachments).toHaveLength(1);
    expect(page1.nextCursor).toBeNull();
  });

  it('supports cursor pagination', async () => {
    const db = new ChatDB();
    const dialog = db.createDialog();
    db.appendMessage(dialog, 'u1', 'm1');
    db.appendMessage(dialog, 'u1', 'm2');
    const m3 = db.appendMessage(dialog, 'u1', 'm3');

    const handler = historyHandler(db);
    const first: any = await callHandler(handler, { params: { dialogId: dialog }, query: { limit: '2' } });
    expect(first.messages).toHaveLength(2);
    const next: any = await callHandler(handler, {
      params: { dialogId: dialog },
      query: { limit: '2', cursor: first.nextCursor },
    });
    expect(next.messages).toHaveLength(1);
    expect(next.messages[0].id).toBe(m3.id);
  });
});
