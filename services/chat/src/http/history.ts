import express from 'express';
import type ChatDB from '../db';

export function historyHandler(db: ChatDB): express.Handler {
  return (req, res) => {
    const { dialogId } = req.params as { dialogId: string };
    const limit = Number((req.query.limit as string) || 20);
    const cursor = req.query.cursor as string | undefined;
    const result = db.getMessages(dialogId, limit, cursor);
    res.json(result);
  };
}

export function createHistoryRouter(db: ChatDB): express.Router {
  const router = express.Router();
  router.get('/dialogs/:dialogId/history', historyHandler(db));
  return router;
}

export default createHistoryRouter;
