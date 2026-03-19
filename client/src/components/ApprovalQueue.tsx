import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { PendingApproval } from "@shared/schema";

interface ApprovalQueueProps {
  approvals: PendingApproval[];
  requireApproval: boolean;
}

const sourceColors: Record<string, string> = {
  earnings: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  news: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  momentum: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  arb: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  crypto: "bg-orange-500/15 text-orange-400 border-orange-500/30",
};

const statusColors: Record<string, string> = {
  pending: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  approved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  rejected: "bg-red-500/15 text-red-400 border-red-500/30",
  expired: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
};

export function ApprovalQueue({ approvals, requireApproval }: ApprovalQueueProps) {
  const pendingCount = approvals.filter(a => a.status === "pending").length;

  return (
    <Card className="border-border/50" data-testid="card-approval-queue">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold text-foreground flex items-center gap-2">
          <span className="text-base">🎯</span>
          Trade Approvals
          <Badge
            variant="secondary"
            className={`ml-auto text-xs ${
              requireApproval
                ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                : "bg-red-500/15 text-red-400 border-red-500/30"
            }`}
            data-testid="badge-approval-mode"
          >
            {requireApproval ? "Required" : "Auto-approve"}
          </Badge>
          {pendingCount > 0 && (
            <Badge
              variant="secondary"
              className="text-xs bg-amber-500/15 text-amber-400 border-amber-500/30 animate-pulse"
              data-testid="badge-pending-count"
            >
              {pendingCount} pending
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {approvals.length === 0 ? (
          <div className="text-center py-6" data-testid="text-no-approvals">
            <p className="text-sm text-muted-foreground">No trade proposals yet</p>
            <p className="text-xs text-muted-foreground/60 mt-1">
              Agents are scanning for edges — proposals will appear here and on Telegram
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {approvals.map((approval) => (
              <div
                key={approval.id}
                className="p-3 rounded-md bg-muted/30 border border-border/30"
                data-testid={`row-approval-${approval.id}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium text-foreground truncate">
                      {approval.label}
                    </p>
                    <div className="flex items-center gap-2 mt-1.5">
                      <Badge
                        variant="secondary"
                        className={`text-[10px] px-1.5 ${sourceColors[approval.source] || ""}`}
                      >
                        {approval.source.toUpperCase()}
                      </Badge>
                      <span className="text-[10px] text-muted-foreground tabular-nums">
                        {approval.side} ${approval.size.toFixed(2)} @ {(approval.market_prob * 100).toFixed(0)}%
                      </span>
                      <span className="text-[10px] text-muted-foreground tabular-nums">
                        edge: {(approval.edge * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1 shrink-0">
                    <Badge
                      variant="secondary"
                      className={`text-[10px] px-1.5 ${statusColors[approval.status] || ""}`}
                      data-testid={`badge-approval-status-${approval.id}`}
                    >
                      {approval.status}
                    </Badge>
                    <span className="text-[10px] text-muted-foreground tabular-nums">
                      score: {approval.score}/100
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
