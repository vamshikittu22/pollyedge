import { useQuery } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import type { BotStatus } from "@shared/schema";
import { BalanceCard } from "@/components/BalanceCard";
import { BotStatusCard } from "@/components/BotStatusCard";
import { RulesPanel } from "@/components/RulesPanel";
import { PnLChart } from "@/components/PnLChart";
import { TradesTable } from "@/components/TradesTable";
import { OpenPositions } from "@/components/OpenPositions";
import { PerplexityAttribution } from "@/components/PerplexityAttribution";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";

function DashboardSkeleton() {
  return (
    <div className="min-h-screen bg-background p-6">
      <div className="flex items-center gap-3 mb-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Skeleton className="h-40 rounded-md" />
        <Skeleton className="h-40 rounded-md" />
        <Skeleton className="h-40 rounded-md" />
      </div>
      <Skeleton className="h-64 rounded-md mb-6" />
      <Skeleton className="h-48 rounded-md" />
    </div>
  );
}

export default function Dashboard() {
  const { data, isLoading, error } = useQuery<BotStatus>({
    queryKey: ["/api/bot/status"],
    queryFn: async () => {
      const res = await apiRequest("GET", "/api/bot/status");
      return res.json();
    },
    refetchInterval: 5000,
    staleTime: 3000,
  });

  if (isLoading) return <DashboardSkeleton />;

  if (error || !data) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-lg font-semibold text-foreground mb-2">
            Connection Error
          </h2>
          <p className="text-muted-foreground text-sm">
            Could not reach the bot API. Make sure the server is running.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-4 md:p-6">
        {/* Header */}
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <svg
              viewBox="0 0 32 32"
              className="w-8 h-8 text-primary"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              aria-label="PollyEdge logo"
            >
              <polygon points="16,2 30,10 30,22 16,30 2,22 2,10" />
              <polyline points="8,14 14,20 24,10" strokeWidth="2.5" />
            </svg>
            <h1 className="text-xl font-bold text-foreground tracking-tight" data-testid="text-title">
              PollyEdge
            </h1>
            <Badge
              variant={data.dry_run ? "secondary" : "default"}
              className={`text-xs font-medium ${
                data.dry_run
                  ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                  : "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
              }`}
              data-testid="badge-mode"
            >
              {data.dry_run ? "DRY RUN" : "LIVE"}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground tabular-nums">
            Refreshes every 5s
          </p>
        </header>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <BalanceCard
            balance={data.balance}
            allTimePnl={data.all_time_pnl}
            totalTrades={data.total_trades}
          />
          <BotStatusCard
            active={data.bot_active}
            dailyPnl={data.daily_pnl}
            openPositions={Object.keys(data.open_positions).length}
            maxPositions={parseInt(data.rules.max_positions)}
          />
          <RulesPanel rules={data.rules} />
        </div>

        {/* Open Positions (if any) */}
        {Object.keys(data.open_positions).length > 0 && (
          <div className="mb-6">
            <OpenPositions positions={data.open_positions} />
          </div>
        )}

        {/* P&L Chart */}
        <div className="mb-6">
          <PnLChart trades={data.trades} />
        </div>

        {/* Trade History */}
        <TradesTable trades={data.trades} />

        <div className="mt-8">
          <PerplexityAttribution />
        </div>
      </div>
    </div>
  );
}
