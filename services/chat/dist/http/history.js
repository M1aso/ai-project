"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.historyHandler = historyHandler;
exports.createHistoryRouter = createHistoryRouter;
const express_1 = __importDefault(require("express"));
function historyHandler(db) {
    return (req, res) => {
        const { dialogId } = req.params;
        const limit = Number(req.query.limit || 20);
        const cursor = req.query.cursor;
        const result = db.getMessages(dialogId, limit, cursor);
        res.json(result);
    };
}
function createHistoryRouter(db) {
    const router = express_1.default.Router();
    router.get('/dialogs/:dialogId/history', historyHandler(db));
    return router;
}
exports.default = createHistoryRouter;
