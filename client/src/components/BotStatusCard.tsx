import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Power, CircleDot } from "lucide-react";

interface BotStatusCardProps {
  active: boolean;
  dailyPnl: number;
  openPositions: number;
  maxPositions: number;
}

export function BotStatusCard({
  active,
  dailyPnl,
  openPositions,
  maxPositions,
}: BotStatusCardProps) {
  const toggleMutation = useMutation({
    mutationFn: async () => {
      const res = await apiRequest("POST", "/api/bot/toggle");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/bot/status"] });
    },
  });

  const dailyPositive = dailyPnl >= 0;

  return (
    <Card className="bg-card border-card-border" data-testid="card-bot-status">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-muted-foreground font-medium">
            Bot Status
          </span>
          <CircleDot
            className={`w-4 h-4 ${active ? "text-emerald-400" : "text-red-400"}`}
          />
        </div>

        <div className="flex items-center gap-2 mb-1">
          <div
            className={`w-2.5 h-2.5 rounded-full ${
              active ? "bg-emerald-400 animate-pulse" : "bg-red-400"
            }`}
          />
          <span className="text-lg font-semibold text-foreground" data-testid="text-bot-status">
            {active ? "Running" : "Stopped"}
          </span>
        </div>

        <div className="flex items-center gap-4 text-sm mb-4">
          <div>
            <span className="text-muted-foreground">Today: </span>
            <span
              className={`font-medium tabular-nums ${
                dailyPositive ? "text-emerald-400" : "text-red-400"
              }`}
              data-testid="text-daily-pnl"
            >
              {dailyPositive ? "+" : ""}${dailyPnl.toFixed(2)}
            </span>
          </div>
          <div className="text-muted-foreground tabular-nums" data-testid="text-positions">
            {openPositions}/{maxPositions} positions
          </div>
        </div>

        <Button
          variant={active ? "destructive" : "default"}
          size="sm"
          className="w-full"
          onClick={() => toggleMutation.mutate()}
          disabled={toggleMutation.isPending}
          data-testid="button-toggle-bot"
        >
          <Power className="w-4 h-4 mr-2" />
          {toggleMutation.isPending
            ? "Switching..."
            : active
            ? "Stop Bot"
            : "Start Bot"}
        </Button>
      </CardContent>
    </Card>
  );
}
