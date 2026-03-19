import { Card, CardContent } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";
import type { Trade } from "@shared/schema";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useMemo } from "react";

interface PnLChartProps {
  trades: Trade[];
}

export function PnLChart({ trades }: PnLChartProps) {
  const chartData = useMemo(() => {
    if (!trades.length) return [];

    let cumPnl = 0;
    return trades.map((t, i) => {
      const pnl = parseFloat(t.pnl) || 0;
      cumPnl += pnl;
      const ts = t.timestamp || "";
      const dateStr = ts.length >= 10 ? ts.substring(5, 10) : `#${i + 1}`;

      return {
        name: dateStr,
        pnl: parseFloat(pnl.toFixed(2)),
        cumulative: parseFloat(cumPnl.toFixed(2)),
      };
    });
  }, [trades]);

  const hasData = chartData.length > 0;
  const lastCum = hasData ? chartData[chartData.length - 1].cumulative : 0;
  const isPositive = lastCum >= 0;

  return (
    <Card className="bg-card border-card-border" data-testid="card-pnl-chart">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">
              Cumulative P&L
            </span>
          </div>
          {hasData && (
            <span
              className={`text-sm font-semibold tabular-nums ${
                isPositive ? "text-emerald-400" : "text-red-400"
              }`}
            >
              {isPositive ? "+" : ""}${lastCum.toFixed(2)}
            </span>
          )}
        </div>

        {!hasData ? (
          <div className="h-48 flex items-center justify-center">
            <p className="text-sm text-muted-foreground">
              No trades yet. Start the bot to see P&L data.
            </p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart
              data={chartData}
              margin={{ top: 4, right: 4, left: -16, bottom: 0 }}
            >
              <defs>
                <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="0%"
                    stopColor={isPositive ? "#34d399" : "#f87171"}
                    stopOpacity={0.3}
                  />
                  <stop
                    offset="100%"
                    stopColor={isPositive ? "#34d399" : "#f87171"}
                    stopOpacity={0.02}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid
                stroke="hsl(217, 33%, 15%)"
                strokeDasharray="3 3"
                vertical={false}
              />
              <XAxis
                dataKey="name"
                tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "hsl(215, 20%, 55%)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(222, 47%, 8%)",
                  border: "1px solid hsl(217, 33%, 15%)",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                labelStyle={{ color: "hsl(215, 20%, 55%)" }}
                formatter={(value: number) => [
                  `$${value.toFixed(2)}`,
                  "Cumulative",
                ]}
              />
              <Area
                type="monotone"
                dataKey="cumulative"
                stroke={isPositive ? "#34d399" : "#f87171"}
                strokeWidth={2}
                fill="url(#pnlGradient)"
                dot={false}
                activeDot={{
                  r: 4,
                  fill: isPositive ? "#34d399" : "#f87171",
                  strokeWidth: 0,
                }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
