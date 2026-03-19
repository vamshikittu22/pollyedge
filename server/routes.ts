import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {

  // GET /api/bot/status — Return full bot status for the dashboard
  app.get("/api/bot/status", async (_req, res) => {
    const state = await storage.getBotState();
    const trades = await storage.getTrades();
    const config = storage.getConfig();

    res.json({
      bot_active: state.bot_active,
      daily_pnl: state.daily_pnl,
      all_time_pnl: state.all_time_pnl,
      balance: config.starting_balance + state.all_time_pnl,
      dry_run: config.dry_run,
      total_trades: state.total_trades,
      open_positions: state.open_positions,
      trades,
      rules: {
        max_trade_pct: String(config.max_trade_pct),
        daily_loss_cap: String(config.daily_loss_cap),
        max_positions: String(config.max_positions),
        min_edge: String(config.min_edge),
      },
    });
  });

  // POST /api/bot/toggle — Toggle bot active/inactive
  app.post("/api/bot/toggle", async (_req, res) => {
    const state = await storage.getBotState();
    state.bot_active = !state.bot_active;
    await storage.saveBotState(state);
    res.json({ bot_active: state.bot_active });
  });

  // POST /api/bot/rules — Update bot trading rules
  app.post("/api/bot/rules", async (req, res) => {
    const { max_trade_pct, daily_loss_cap, max_positions, min_edge } = req.body;
    storage.updateConfig({
      max_trade_pct: max_trade_pct ? parseFloat(max_trade_pct) : undefined,
      daily_loss_cap: daily_loss_cap ? parseFloat(daily_loss_cap) : undefined,
      max_positions: max_positions ? parseInt(max_positions) : undefined,
      min_edge: min_edge ? parseFloat(min_edge) : undefined,
    });
    res.json({ status: "ok" });
  });

  return httpServer;
}
