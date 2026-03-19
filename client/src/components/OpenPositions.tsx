import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Crosshair } from "lucide-react";
import type { BotStatus } from "@shared/schema";

interface OpenPositionsProps {
  positions: BotStatus["open_positions"];
}

export function OpenPositions({ positions }: OpenPositionsProps) {
  const entries = Object.entries(positions);

  if (entries.length === 0) return null;

  return (
    <Card className="bg-card border-card-border" data-testid="card-positions">
      <CardContent className="p-5">
        <div className="flex items-center gap-2 mb-4">
          <Crosshair className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium text-foreground">
            Open Positions
          </span>
          <Badge variant="secondary" className="text-xs ml-auto">
            {entries.length} active
          </Badge>
        </div>

        <div className="space-y-2">
          {entries.map(([tokenId, pos]) => (
            <div
              key={tokenId}
              className="flex items-center justify-between p-3 rounded-md bg-accent/50 border border-border"
              data-testid={`position-${tokenId.substring(0, 8)}`}
            >
              <div className="flex items-center gap-3">
                <Badge
                  className={`text-xs font-medium ${
                    pos.side === "BUY"
                      ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                      : "bg-red-500/15 text-red-400 border-red-500/30"
                  }`}
                >
                  {pos.side}
                </Badge>
                <span className="text-sm text-foreground truncate max-w-[200px]">
                  {pos.label}
                </span>
              </div>
              <div className="flex items-center gap-4 text-sm tabular-nums">
                <span className="text-muted-foreground">
                  ${pos.size.toFixed(2)}
                </span>
                <span className="text-foreground font-medium">
                  @ {pos.entry_price.toFixed(4)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
