import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";

// Bot state table — key-value store for bot persistence
export const botState = sqliteTable("bot_state", {
  key: text("key").primaryKey(),
  value: text("value").notNull(), // JSON-encoded
});

// Open positions table — one row per active position
export const openPositions = sqliteTable("open_positions", {
  tokenId: text("token_id").primaryKey(),
  side: text("side").notNull(), // "BUY" or "SELL"
  size: real("size").notNull(),
  entryPrice: real("entry_price").notNull(),
  label: text("label").notNull(),
  openedAt: text("opened_at").notNull(), // ISO timestamp
});

// Agent status table — one row per agent
export const agentStatus = sqliteTable("agent_status", {
  name: text("name").primaryKey(),
  status: text("status").notNull(), // "running" | "stopped" | "error"
  lastScan: text("last_scan").notNull(), // ISO timestamp
  signalsFound: integer("signals_found").notNull().default(0),
});

// Pending approvals table — approval queue for trades
export const pendingApprovals = sqliteTable("pending_approvals", {
  id: text("id").primaryKey(),
  label: text("label").notNull(),
  side: text("side").notNull(),
  size: real("size").notNull(),
  edge: real("edge").notNull(),
  source: text("source").notNull(),
  score: integer("score").notNull(),
  marketProb: real("market_prob").notNull(),
  modelProb: real("model_prob").notNull(),
  timestamp: text("timestamp").notNull(), // ISO timestamp
  status: text("status").notNull().default("pending"), // "pending" | "approved" | "rejected" | "expired"
});

// Trades table — closed trades history
export const trades = sqliteTable("trades", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  tokenId: text("token_id").notNull(),
  label: text("label").notNull(),
  exitPrice: real("exit_price").notNull(),
  pnl: real("pnl").notNull(),
  closedAt: text("closed_at").notNull(), // ISO timestamp
});

// TypeScript types derived from schema
export type BotState = typeof botState.$inferSelect;
export type NewBotState = typeof botState.$inferInsert;

export type OpenPosition = typeof openPositions.$inferSelect;
export type NewOpenPosition = typeof openPositions.$inferInsert;

export type AgentStatus = typeof agentStatus.$inferSelect;
export type NewAgentStatus = typeof agentStatus.$inferInsert;

export type PendingApproval = typeof pendingApprovals.$inferSelect;
export type NewPendingApproval = typeof pendingApprovals.$inferInsert;

export type Trade = typeof trades.$inferSelect;
export type NewTrade = typeof trades.$inferInsert;
