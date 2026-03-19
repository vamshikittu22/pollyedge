import { Card, CardContent } from "@/components/ui/card";
import { Wallet, TrendingUp, TrendingDown, Activity } from "lucide-react";

interface BalanceCardProps {
  balance: number;
  allTimePnl: number;
  totalTrades: number;
}

export function BalanceCard({ balance, allTimePnl, totalTrades }: BalanceCardProps) {
  const pnlPositive = allTimePnl >= 0;

  return (
    <Card className="bg-card border-card-border" data-testid="card-balance">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-muted-foreground font-medium">
            Wallet Balance
          </span>
          <Wallet className="w-4 h-4 text-muted-foreground" />
        </div>

        <div className="tabular-nums">
          <p className="text-2xl font-bold text-foreground tracking-tight" data-testid="text-balance">
            ${balance.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
        </div>

        <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
          <div className="flex items-center gap-1.5">
            {pnlPositive ? (
              <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <TrendingDown className="w-3.5 h-3.5 text-red-400" />
            )}
            <span
              className={`text-sm font-medium tabular-nums ${
                pnlPositive ? "text-emerald-400" : "text-red-400"
              }`}
              data-testid="text-all-time-pnl"
            >
              {pnlPositive ? "+" : ""}
              ${allTimePnl.toFixed(2)}
            </span>
            <span className="text-xs text-muted-foreground">all-time</span>
          </div>

          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-sm text-muted-foreground tabular-nums" data-testid="text-total-trades">
              {totalTrades} trades
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
