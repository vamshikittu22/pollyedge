import { Card, CardContent } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ScrollArea } from "@/components/ui/scroll-area";
import { History } from "lucide-react";
import type { Trade } from "@shared/schema";

interface TradesTableProps {
  trades: Trade[];
}

export function TradesTable({ trades }: TradesTableProps) {
  // Show most recent first
  const sortedTrades = [...trades].reverse();

  return (
    <Card className="bg-card border-card-border" data-testid="card-trades">
      <CardContent className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <History className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium text-foreground">
            Trade History
          </span>
          <span className="text-xs text-muted-foreground ml-auto tabular-nums">
            {trades.length} trades
          </span>
        </div>

        {sortedTrades.length === 0 ? (
          <div className="h-24 flex items-center justify-center">
            <p className="text-sm text-muted-foreground">
              No completed trades yet.
            </p>
          </div>
        ) : (
          <ScrollArea className="max-h-80">
            <Table>
              <TableHeader>
                <TableRow className="border-border hover:bg-transparent">
                  <TableHead className="text-xs text-muted-foreground font-medium">
                    Time
                  </TableHead>
                  <TableHead className="text-xs text-muted-foreground font-medium">
                    Market
                  </TableHead>
                  <TableHead className="text-xs text-muted-foreground font-medium text-right">
                    Exit Price
                  </TableHead>
                  <TableHead className="text-xs text-muted-foreground font-medium text-right">
                    P&L
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedTrades.map((trade, i) => {
                  const pnl = parseFloat(trade.pnl) || 0;
                  const positive = pnl >= 0;
                  const ts = trade.timestamp || "";
                  const timeStr = ts.length >= 16
                    ? ts.substring(5, 16).replace("T", " ")
                    : ts;

                  return (
                    <TableRow
                      key={`${trade.token_id}-${i}`}
                      className="border-border"
                      data-testid={`row-trade-${i}`}
                    >
                      <TableCell className="text-xs text-muted-foreground tabular-nums py-2.5">
                        {timeStr}
                      </TableCell>
                      <TableCell className="text-sm text-foreground py-2.5 max-w-[200px] truncate">
                        {trade.label}
                      </TableCell>
                      <TableCell className="text-sm text-foreground tabular-nums text-right py-2.5">
                        {parseFloat(trade.exit_price).toFixed(4)}
                      </TableCell>
                      <TableCell
                        className={`text-sm font-medium tabular-nums text-right py-2.5 ${
                          positive ? "text-emerald-400" : "text-red-400"
                        }`}
                      >
                        {positive ? "+" : ""}${pnl.toFixed(2)}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
