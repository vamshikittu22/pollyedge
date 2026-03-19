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
});

export type BotStatus = z.infer<typeof botStatusSchema>;

export type Trade = BotStatus["trades"][number];
export type OpenPosition = BotStatus["open_positions"][string];
export type Rules = BotStatus["rules"];
