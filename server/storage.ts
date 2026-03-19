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

interface BotConfig {
  dry_run: boolean;
  starting_balance: number;
  max_trade_pct: number;
  daily_loss_cap: number;
  max_positions: number;
  min_edge: number;
}

const STATE_FILE = path.resolve("bot_state.json");
const TRADES_FILE = path.resolve("logs/trades.csv");

const DEFAULT_STATE: BotState = {
  daily_pnl: 0,
  daily_date: new Date().toISOString().split("T")[0],
  open_positions: {},
  total_trades: 0,
  all_time_pnl: 0,
  bot_active: false,
};

// In-memory config (reads from env-like defaults)
let config: BotConfig = {
  dry_run: true,
  starting_balance: 500,
  max_trade_pct: 0.03,
  daily_loss_cap: 0.10,
  max_positions: 3,
  min_edge: 0.08,
};

export interface IStorage {
  getBotState(): Promise<BotState>;
  saveBotState(state: BotState): Promise<void>;
  getTrades(): Promise<Trade[]>;
  getConfig(): BotConfig;
  updateConfig(partial: Partial<BotConfig>): void;
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
}

export const storage = new MemStorage();
