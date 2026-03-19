import { Card, CardContent } from "@/components/ui/card";
import { Shield } from "lucide-react";
import type { Rules } from "@shared/schema";

interface RulesPanelProps {
  rules: Rules;
}

export function RulesPanel({ rules }: RulesPanelProps) {
  const ruleItems = [
    {
      label: "Max per trade",
      value: `${(parseFloat(rules.max_trade_pct) * 100).toFixed(0)}%`,
    },
    {
      label: "Daily loss cap",
      value: `${(parseFloat(rules.daily_loss_cap) * 100).toFixed(0)}%`,
    },
    {
      label: "Max positions",
      value: rules.max_positions,
    },
    {
      label: "Min edge",
      value: `${(parseFloat(rules.min_edge) * 100).toFixed(0)}%`,
    },
  ];

  return (
    <Card className="bg-card border-card-border" data-testid="card-rules">
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-muted-foreground font-medium">
            Safety Rules
          </span>
          <Shield className="w-4 h-4 text-muted-foreground" />
        </div>

        <div className="space-y-2.5">
          {ruleItems.map((rule) => (
            <div
              key={rule.label}
              className="flex items-center justify-between"
            >
              <span className="text-sm text-muted-foreground">
                {rule.label}
              </span>
              <span className="text-sm font-medium text-foreground tabular-nums" data-testid={`text-rule-${rule.label.toLowerCase().replace(/\s/g, '-')}`}>
                {rule.value}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
