import fs from "fs";
import path from "path";

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
  timestamp: string;
  token_id: string;
  label: string;
  exit_price: string;
  pnl: string;
}

interface PendingApproval {
  id: string;
  label: string;
  side: string;
  size: number;
  edge: number;
  source: string;
  score: number;
  market_prob: number;
  model_prob: number;
  timestamp: string;
  status: "pending" | "approved" | "rejected" | "expired";
}

interface AgentInfo {
  name: string;
  status: "running" | "stopped" | "error";
  last_scan: string;
  signals_found: number;
}

interface BotConfig {
  dry_run: boolean;
  starting_balance: number;
  max_trade_pct: number;
  daily_loss_cap: number;
  max_positions: number;
  min_edge: number;
  require_approval: boolean;
}

const STATE_FILE = path.resolve("bot_state.json");
const TRADES_FILE = path.resolve("logs/trades.csv");
const APPROVALS_FILE = path.resolve("pending_approvals.json");
const AGENTS_FILE = path.resolve("agent_status.json");

const DEFAULT_STATE: BotState = {
  daily_pnl: 0,
  daily_date: new Date().toISOString().split("T")[0],
  open_positions: {},
  total_trades: 0,
  all_time_pnl: 0,
  bot_active: false,
};

// In-memory config (reads from environment)
let config: BotConfig = {
  dry_run: (process.env.DRY_RUN ?? "true").toLowerCase() === "true",
  starting_balance: parseFloat(process.env.STARTING_BALANCE ?? "10"),
  max_trade_pct: parseFloat(process.env.MAX_TRADE_PCT ?? "0.50"),
  daily_loss_cap: parseFloat(process.env.DAILY_LOSS_CAP ?? "0.30"),
  max_positions: parseInt(process.env.MAX_POSITIONS ?? "1"),
  min_edge: parseFloat(process.env.MIN_EDGE ?? "0.08"),
  require_approval: (process.env.REQUIRE_APPROVAL ?? "true").toLowerCase() === "true",
};

export interface IStorage {
  getBotState(): Promise<BotState>;
  saveBotState(state: BotState): Promise<void>;
  getTrades(): Promise<Trade[]>;
  getConfig(): BotConfig;
  updateConfig(partial: Partial<BotConfig>): void;
  getPendingApprovals(): Promise<PendingApproval[]>;
  getAgentStatus(): Promise<AgentInfo[]>;
}

export class MemStorage implements IStorage {
  private state: BotState;

  constructor() {
    // Try to load existing state from disk
    this.state = this.loadFromDisk();
  }

  private loadFromDisk(): BotState {
    try {
      if (fs.existsSync(STATE_FILE)) {
        const raw = fs.readFileSync(STATE_FILE, "utf-8");
        return JSON.parse(raw);
      }
    } catch {
      // Fall through to default
    }
    return { ...DEFAULT_STATE };
  }

  async getBotState(): Promise<BotState> {
    // Re-read from disk each time (bot may have updated it)
    try {
      if (fs.existsSync(STATE_FILE)) {
        const raw = fs.readFileSync(STATE_FILE, "utf-8");
        this.state = JSON.parse(raw);
      }
    } catch {
      // Use cached state
    }
    return this.state;
  }

  async saveBotState(state: BotState): Promise<void> {
    this.state = state;
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  }

  async getTrades(): Promise<Trade[]> {
    try {
      if (!fs.existsSync(TRADES_FILE)) return [];
      const raw = fs.readFileSync(TRADES_FILE, "utf-8");
      const lines = raw.trim().split("\n");
      if (lines.length <= 1) return [];

      const headers = lines[0].split(",");
      const trades: Trade[] = [];

      for (let i = Math.max(1, lines.length - 50); i < lines.length; i++) {
        const values = lines[i].split(",");
        const trade: Record<string, string> = {};
        headers.forEach((h, idx) => {
          trade[h.trim()] = (values[idx] || "").trim();
        });
        trades.push(trade as unknown as Trade);
      }

      return trades;
    } catch {
      return [];
    }
  }

  getConfig(): BotConfig {
    return { ...config };
  }

  updateConfig(partial: Partial<BotConfig>): void {
    config = { ...config, ...partial };
  }

  async getPendingApprovals(): Promise<PendingApproval[]> {
    try {
      if (!fs.existsSync(APPROVALS_FILE)) return [];
      const raw = fs.readFileSync(APPROVALS_FILE, "utf-8");
      return JSON.parse(raw);
    } catch {
      return [];
    }
  }

  async getAgentStatus(): Promise<AgentInfo[]> {
    try {
      if (!fs.existsSync(AGENTS_FILE)) {
        // Return default agent list when bot hasn't started yet
        return [
          { name: "EarningsAgent", status: "stopped", last_scan: "-", signals_found: 0 },
          { name: "NewsAgent", status: "stopped", last_scan: "-", signals_found: 0 },
          { name: "MomentumAgent", status: "stopped", last_scan: "-", signals_found: 0 },
          { name: "ArbAgent", status: "stopped", last_scan: "-", signals_found: 0 },
          { name: "CryptoAgent", status: "stopped", last_scan: "-", signals_found: 0 },
        ];
      }
      const raw = fs.readFileSync(AGENTS_FILE, "utf-8");
      return JSON.parse(raw);
    } catch {
      return [];
    }
  }
}

export const storage = new MemStorage();
