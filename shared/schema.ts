import { z } from "zod";

// Bot status response from the API
export const botStatusSchema = z.object({
  bot_active: z.boolean(),
  daily_pnl: z.number(),
  all_time_pnl: z.number(),
  balance: z.number(),
  dry_run: z.boolean(),
  total_trades: z.number(),
  open_positions: z.record(z.string(), z.object({
    side: z.string(),
    size: z.number(),
    entry_price: z.number(),
    label: z.string(),
  })),
  trades: z.array(z.object({
    timestamp: z.string(),
    token_id: z.string(),
    label: z.string(),
    exit_price: z.string(),
    pnl: z.string(),
  })),
  rules: z.object({
    max_trade_pct: z.string(),
    daily_loss_cap: z.string(),
    max_positions: z.string(),
    min_edge: z.string(),
  }),
  // v2.0: approval queue and agent status
  pending_approvals: z.array(z.object({
    id: z.string(),
    label: z.string(),
    side: z.string(),
    size: z.number(),
    edge: z.number(),
    source: z.string(),
    score: z.number(),
    market_prob: z.number(),
    model_prob: z.number(),
    timestamp: z.string(),
    status: z.enum(["pending", "approved", "rejected", "expired"]),
  })).optional().default([]),
  agents: z.array(z.object({
    name: z.string(),
    status: z.enum(["running", "stopped", "error"]),
    last_scan: z.string(),
    signals_found: z.number(),
  })).optional().default([]),
  require_approval: z.boolean().optional().default(true),
});

export type BotStatus = z.infer<typeof botStatusSchema>;

export type Trade = BotStatus["trades"][number];
export type OpenPosition = BotStatus["open_positions"][string];
export type Rules = BotStatus["rules"];
export type PendingApproval = NonNullable<BotStatus["pending_approvals"]>[number];
export type AgentInfo = NonNullable<BotStatus["agents"]>[number];
