import Database from "better-sqlite3";
import { eq, desc } from "drizzle-orm";
import { drizzle } from "drizzle-orm/better-sqlite3";
import * as schema from "../shared/schema";

// Bot state shape (mirrors Python bot's bot_state.json)
interface BotState {
  daily_pnl: number;
  daily_date: string;
  open_positions: Record<string, {
    side: string;
    size: number;
    entry_price: number;
    label: string;
  }>;
  total_trades: number;
  all_time_pnl: number;
  bot_active: boolean;
}

interface Trade {
  id: number;
  tokenId: string;
  label: string;
  exitPrice: number;
  pnl: number;
  closedAt: string;
}

interface PendingApproval {
  id: string;
  label: string;
  side: string;
  size: number;
  edge: number;
  source: string;
  score: number;
  marketProb: number;
  modelProb: number;
  timestamp: string;
  analysis: string | null;
  status: "pending" | "approved" | "rejected" | "expired";
}

interface AgentInfo {
  name: string;
  status: "running" | "stopped" | "error";
  lastScan: string;
  signalsFound: number;
}

interface BotConfig {
  dry_run: boolean;
  starting_balance: number;
  max_trade_pct: number;
  daily_loss_cap: number;
  max_positions: number;
  min_edge: number;
  require_approval: boolean;
  conviction_threshold: number;
}

// In-memory config (reads from environment)
let config: BotConfig = {
  dry_run: (process.env.DRY_RUN ?? "true").toLowerCase() === "true",
  starting_balance: parseFloat(process.env.STARTING_BALANCE ?? "10"),
  max_trade_pct: parseFloat(process.env.MAX_TRADE_PCT ?? "0.50"),
  daily_loss_cap: parseFloat(process.env.DAILY_LOSS_CAP ?? "0.30"),
  max_positions: parseInt(process.env.MAX_POSITIONS ?? "1"),
  min_edge: parseFloat(process.env.MIN_EDGE ?? "0.08"),
  require_approval: (process.env.REQUIRE_APPROVAL ?? "true").toLowerCase() === "true",
  conviction_threshold: parseFloat(process.env.CONVICTION_THRESHOLD ?? "0"),
};

export interface IStorage {
  getBotState(): Promise<BotState>;
  saveBotState(state: BotState): Promise<void>;
  getTrades(): Promise<Trade[]>;
  getConfig(): BotConfig;
  updateConfig(partial: Partial<BotConfig>): void;
  getPendingApprovals(): Promise<PendingApproval[]>;
  resolveApproval(id: string, status: string): Promise<void>;
  getAgentStatus(): Promise<AgentInfo[]>;
}

export class SQLiteStorage implements IStorage {
  private db: ReturnType<typeof drizzle>;
  private rawDb: Database.Database;

  constructor() {
    const sqlite = new Database("data/pollyedge.db");
    this.rawDb = sqlite;
    this.db = drizzle(sqlite, { schema });
  }

  async getBotState(): Promise<BotState> {
    // Read from SQLite bot_state table
    const rows = this.db.select().from(schema.botState).all();
    const state: Record<string, unknown> = {};
    
    for (const row of rows) {
      try {
        state[row.key] = JSON.parse(row.value);
      } catch {
        state[row.key] = row.value;
      }
    }

    // Read open_positions from separate table
    const positions = this.db.select().from(schema.openPositions).all();
    const openPositions: BotState["open_positions"] = {};
    
    for (const pos of positions) {
      openPositions[pos.tokenId] = {
        side: pos.side,
        size: pos.size,
        entry_price: pos.entryPrice,
        label: pos.label,
      };
    }

    return {
      daily_pnl: (state.daily_pnl as number) ?? 0,
      daily_date: (state.daily_date as string) ?? new Date().toISOString().split("T")[0],
      open_positions: openPositions,
      total_trades: (state.total_trades as number) ?? 0,
      all_time_pnl: (state.all_time_pnl as number) ?? 0,
      bot_active: (state.bot_active as boolean) ?? false,
    };
  }

  async saveBotState(state: BotState): Promise<void> {
    // Save to SQLite bot_state table
    const stateData = {
      daily_pnl: state.daily_pnl,
      daily_date: state.daily_date,
      total_trades: state.total_trades,
      all_time_pnl: state.all_time_pnl,
      bot_active: state.bot_active,
    };

    for (const [key, value] of Object.entries(stateData)) {
      this.db.insert(schema.botState)
        .values({ key, value: JSON.stringify(value) })
        .onConflictDoUpdate({
          target: schema.botState.key,
          set: { value: JSON.stringify(value) },
        })
        .run();
    }

    // Note: open_positions are managed separately via add/remove_position
  }

  async getTrades(): Promise<Trade[]> {
    // Read from SQLite trades table
    const rows = this.db.select()
      .from(schema.trades)
      .orderBy(desc(schema.trades.closedAt))
      .limit(50)
      .all();
    
    return rows.map(row => ({
      id: row.id,
      tokenId: row.tokenId,
      label: row.label,
      exitPrice: row.exitPrice,
      pnl: row.pnl,
      closedAt: row.closedAt,
    }));
  }

  getConfig(): BotConfig {
    return { ...config };
  }

  updateConfig(partial: Partial<BotConfig>): void {
    config = { ...config, ...partial };
  }

  async getPendingApprovals(): Promise<PendingApproval[]> {
    // Read from SQLite pending_approvals table
    const rows = this.db.select()
      .from(schema.pendingApprovals)
      .orderBy(desc(schema.pendingApprovals.timestamp))
      .all();
    
    return rows.map(row => ({
      id: row.id,
      label: row.label,
      side: row.side,
      size: row.size,
      edge: row.edge,
      source: row.source,
      score: row.score,
      marketProb: row.marketProb,
      modelProb: row.modelProb,
      timestamp: row.timestamp,
      analysis: row.analysis,
      status: row.status as PendingApproval["status"],
    }));
  }

  async resolveApproval(id: string, status: string): Promise<void> {
    this.db.update(schema.pendingApprovals)
      .set({ status })
      .where(eq(schema.pendingApprovals.id, id))
      .run();
  }

  async getAgentStatus(): Promise<AgentInfo[]> {
    // Read from SQLite agent_status table
    const rows = this.db.select()
      .from(schema.agentStatus)
      .orderBy(schema.agentStatus.name)
      .all();
    
    if (rows.length === 0) {
      // Return default agent list when bot hasn't started yet
      return [
        { name: "EarningsAgent", status: "stopped", lastScan: "-", signalsFound: 0 },
        { name: "NewsAgent", status: "stopped", lastScan: "-", signalsFound: 0 },
        { name: "MomentumAgent", status: "stopped", lastScan: "-", signalsFound: 0 },
        { name: "ArbAgent", status: "stopped", lastScan: "-", signalsFound: 0 },
        { name: "CryptoAgent", status: "stopped", lastScan: "-", signalsFound: 0 },
      ];
    }
    
    return rows.map(row => ({
      name: row.name,
      status: row.status as AgentInfo["status"],
      lastScan: row.lastScan,
      signalsFound: row.signalsFound,
    }));
  }

  async getConvictionThreshold(): Promise<number> {
    // Read from SQLite bot_state table
    const rows = this.db.select()
      .from(schema.botState)
      .where(eq(schema.botState.key, "conviction_threshold"))
      .all();
    
    if (rows.length === 0 || !rows[0].value) {
      return 0;
    }
    
    try {
      return parseFloat(rows[0].value);
    } catch {
      return 0;
    }
  }

  async setConvictionThreshold(value: number): Promise<void> {
    // Store in SQLite bot_state table
    this.db.insert(schema.botState)
      .values({ key: "conviction_threshold", value: String(value) })
      .onConflictDoUpdate({
        target: schema.botState.key,
        set: { value: String(value) },
      })
      .run();
    
    // Update in-memory config
    config.conviction_threshold = value;
  }

}

// Backward compatibility: export as MemStorage
export const MemStorage = SQLiteStorage;
export const storage = new SQLiteStorage();

