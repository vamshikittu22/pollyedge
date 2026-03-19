import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AgentInfo } from "@shared/schema";

interface AgentSwarmPanelProps {
  agents: AgentInfo[];
}

const agentIcons: Record<string, string> = {
  EarningsAgent: "📊",
  NewsAgent: "📰",
  MomentumAgent: "📈",
  ArbAgent: "⚖️",
  CryptoAgent: "🪙",
};

const agentDescriptions: Record<string, string> = {
  EarningsAgent: "Daloopa + Yahoo + Alpha Vantage",
  NewsAgent: "NewsAPI sentiment analysis",
  MomentumAgent: "Price mean-reversion detection",
  ArbAgent: "YES+NO arbitrage scanner",
  CryptoAgent: "CoinGecko momentum signals",
};

export function AgentSwarmPanel({ agents }: AgentSwarmPanelProps) {
  return (
    <Card className="border-border/50" data-testid="card-agent-swarm">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
          <span className="text-base">🐝</span>
          Agent Swarm
          <Badge
            variant="secondary"
            className="ml-auto text-xs bg-primary/10 text-primary border-primary/20"
            data-testid="badge-agent-count"
          >
            {agents.filter(a => a.status === "running").length}/{agents.length} active
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/30 border border-border/30"
            data-testid={`row-agent-${agent.name}`}
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-sm shrink-0">{agentIcons[agent.name] || "🤖"}</span>
              <div className="min-w-0">
                <p className="text-xs font-medium text-foreground truncate">{agent.name}</p>
                <p className="text-[10px] text-muted-foreground truncate">
                  {agentDescriptions[agent.name] || "Signal agent"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              {agent.signals_found > 0 && (
                <span className="text-[10px] text-muted-foreground tabular-nums">
                  {agent.signals_found} signals
                </span>
              )}
              <Badge
                variant="secondary"
                className={`text-[10px] px-1.5 ${
                  agent.status === "running"
                    ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                    : agent.status === "error"
                    ? "bg-red-500/15 text-red-400 border-red-500/30"
                    : "bg-zinc-500/15 text-zinc-400 border-zinc-500/30"
                }`}
                data-testid={`badge-agent-status-${agent.name}`}
              >
                {agent.status}
              </Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
