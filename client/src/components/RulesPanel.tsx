import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Shield } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import type { PendingApproval } from "@shared/schema";

interface RulesPanelProps {
  rules: any;
  approvals?: PendingApproval[];
}

export function RulesPanel({ rules, approvals = [] }: RulesPanelProps) {
  const [minEdge, setMinEdge] = useState<number>(parseFloat(rules.min_edge));
  const [threshold, setThreshold] = useState<number>(parseFloat(rules.conviction_threshold) || 0);
  const queryClient = useQueryClient();

  useEffect(() => {
    setMinEdge(parseFloat(rules.min_edge));
    setThreshold(parseFloat(rules.conviction_threshold) || 0);
  }, [rules.min_edge, rules.conviction_threshold]);

  const rulesMutation = useMutation({
    mutationFn: (newMinEdge: number) => 
      fetch("/api/bot/rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ min_edge: newMinEdge })
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["/api/bot/status"] }),
  });

  const thresholdMutation = useMutation({
    mutationFn: (newThreshold: number) => 
      fetch("/api/bot/threshold", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conviction_threshold: newThreshold })
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["/api/bot/status"] }),
  });

  const wouldPass = approvals.filter(a => a.edge >= minEdge).length;
  const wouldPassThreshold = approvals.filter(a => a.score >= threshold).length;
  
  const handleEdgeCommit = (val: number[]) => {
    rulesMutation.mutate(val[0]);
  };

  const handleThresholdCommit = (val: number[]) => {
    thresholdMutation.mutate(val[0]);
  };

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

          <div className="pt-2 border-t border-border mt-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Min Edge</span>
              <span className="text-sm font-medium text-foreground tabular-nums">{(minEdge * 100).toFixed(0)}%</span>
            </div>
            <Slider 
              value={[minEdge]} 
              onValueChange={(v) => setMinEdge(v[0])} 
              onValueCommit={handleEdgeCommit}
              min={0.05} 
              max={0.20} 
              step={0.01} 
              className="py-2"
            />
            {approvals.length > 0 && (
              <p className="text-[10px] text-muted-foreground mt-2 text-center font-medium">
                Live preview: {wouldPass} / {approvals.length} recent signals would pass
              </p>
            )}
          </div>

          <div className="pt-2 border-t border-border mt-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Conviction Threshold</span>
              <span className="text-sm font-medium text-foreground tabular-nums">{threshold}/100</span>
            </div>
            <p className="text-[10px] text-muted-foreground mb-2">
              Only show signals scoring above this threshold
            </p>
            <Slider 
              value={[threshold]} 
              onValueChange={(v) => setThreshold(v[0])} 
              onValueCommit={handleThresholdCommit}
              min={0} 
              max={100} 
              step={5} 
              className="py-2"
            />
            {approvals.length > 0 && (
              <p className="text-[10px] text-muted-foreground mt-2 text-center font-medium">
                Live preview: {wouldPassThreshold} / {approvals.length} signals would pass
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
