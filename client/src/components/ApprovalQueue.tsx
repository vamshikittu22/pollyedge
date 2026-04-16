import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ChevronDown, ChevronUp, Activity } from "lucide-react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import type { PendingApproval } from "@shared/schema"

// Analysis data structure stored in JSON
interface AnalysisData {
  model_prob?: number;
  market_prob?: number;
  edge?: number;
  factors?: string[];
  confidence?: number;
  reasoning?: string;
}

interface ApprovalQueueProps {
  approvals: PendingApproval[]
  requireApproval: boolean
}

const sourceColors: Record<string, string> = {
  earnings: "bg-blue-500/15 text-blue-400 border-blue-500/30",
  news: "bg-purple-500/15 text-purple-400 border-purple-500/30",
  momentum: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  arb: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  crypto: "bg-orange-500/15 text-orange-400 border-orange-500/30",
}

const statusColors: Record<string, string> = {
  pending: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  approved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  rejected: "bg-red-500/15 text-red-400 border-red-500/30",
  expired: "bg-zinc-500/15 text-zinc-400 border-zinc-500/30",
}

// Parse analysis JSON string into structured object
function parseAnalysis(analysisStr: string | null | undefined): AnalysisData | null {
  if (!analysisStr) return null;
  try {
    return JSON.parse(analysisStr) as AnalysisData;
  } catch {
    return null;
  }
}

// Analysis breakdown display component
function AnalysisBreakdown({ analysis, expanded }: { analysis: AnalysisData; expanded: boolean }) {
  const modelProb = (analysis.model_prob ?? 0) * 100;
  const marketProb = (analysis.market_prob ?? 0) * 100;
  const edgeVal = (analysis.edge ?? 0) * 100;
  const confidence = analysis.confidence ?? 0;

  return (
    <div className="mt-2 p-2 rounded bg-background/50 border border-border/20 space-y-1.5">
      <div className="flex items-center gap-3 text-[10px]">
        <div className="flex-1">
          <span className="text-muted-foreground">Model</span>
          <span className="ml-1 font-mono text-foreground">{modelProb.toFixed(1)}%</span>
        </div>
        <div className="flex-1">
          <span className="text-muted-foreground">Market</span>
          <span className="ml-1 font-mono text-foreground">{marketProb.toFixed(1)}%</span>
        </div>
        <div className="flex-1">
          <span className="text-muted-foreground">Edge</span>
          <span className={`ml-1 font-mono ${edgeVal >= 0 ? "text-emerald-400" : "text-red-400"}`}>
            {edgeVal >= 0 ? "+" : ""}{edgeVal.toFixed(1)}%
          </span>
        </div>
        <div className="flex-1">
          <span className="text-muted-foreground">Conf.</span>
          <span className="ml-1 font-mono text-foreground">{confidence.toFixed(0)}/100</span>
        </div>
      </div>
      {analysis.factors && analysis.factors.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-1.5">
          {analysis.factors.map((factor, i) => (
            <span
              key={i}
              className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30"
            >
              {factor}
            </span>
          ))}
        </div>
      )}
      {analysis.reasoning && (
        <p className="text-[9px] text-muted-foreground mt-1.5 italic">
          {analysis.reasoning}
        </p>
      )}
    </div>
  )
}

export function ApprovalQueue({ approvals, requireApproval }: ApprovalQueueProps) {
  const pendingCount = approvals.filter(a => a.status === "pending").length
  const queryClient = useQueryClient()

  const approveMutation = useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/approvals/${id}/approve`, { method: "POST" }).then(r => {
        if (!r.ok) throw new Error("Approve failed")
        return r.json()
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["/api/bot/status"] }),
  })

  const rejectMutation = useMutation({
    mutationFn: (id: string) =>
      fetch(`/api/approvals/${id}/reject`, { method: "POST" }).then(r => {
        if (!r.ok) throw new Error("Reject failed")
        return r.json()
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["/api/bot/status"] }),
  })

  const isActioning = approveMutation.isPending || rejectMutation.isPending

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
            {approvals.map((approval) => {
              const parsedAnalysis = parseAnalysis(approval.analysis);
              const hasAnalysis = !!parsedAnalysis;

              return (
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
                          {approval.side} ${approval.size.toFixed(2)} @ {(approval.marketProb * 100).toFixed(0)}%
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

                  {/* Analysis breakdown with collapsible */}
                  {hasAnalysis ? (
                    <Collapsible className="mt-2">
                      <CollapsibleTrigger className="flex items-center gap-1 text-[10px] text-muted-foreground hover:text-foreground transition-colors">
                        <Activity className="w-3 h-3" />
                        <span>View Analysis</span>
                        <ChevronDown className="w-3 h-3 data-[state=open]:hidden" />
                        <ChevronUp className="w-3 h-3 hidden data-[state=open]:block" />
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <AnalysisBreakdown analysis={parsedAnalysis!} expanded={false} />
                      </CollapsibleContent>
                    </Collapsible>
                  ) : approval.analysis ? (
                    // Fallback for legacy plain text analysis
                    <p className="text-[11px] text-muted-foreground mt-0.5 whitespace-pre-wrap">
                      ↳ {approval.analysis}
                    </p>
                  ) : null}

                  {approval.status === "pending" && (
                    <div className="flex gap-2 mt-2 pt-2 border-t border-border/20">
                      <button
                        onClick={() => approveMutation.mutate(approval.id)}
                        disabled={isActioning}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs rounded font-bold transition-colors"
                        data-testid={`btn-approve-${approval.id}`}
                      >
                        ✅ Approve
                      </button>
                      <button
                        onClick={() => rejectMutation.mutate(approval.id)}
                        disabled={isActioning}
                        className="px-3 py-1.5 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs rounded font-bold transition-colors"
                        data-testid={`btn-reject-${approval.id}`}
                      >
                        ❌ Reject
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
