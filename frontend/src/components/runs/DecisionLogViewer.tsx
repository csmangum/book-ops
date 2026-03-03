"use client";

import { EmptyState } from "@/components/shared/EmptyState";

export function DecisionLogViewer({
  runDetail,
}: {
  runDetail?: Record<string, unknown> | null;
}) {
  const log = runDetail?.decision_log as
    | {
        run_id?: string;
        scope?: string;
        gate?: { status?: string; message?: string };
        analysis_counts?: { total_findings?: number; hard_findings?: number; soft_findings?: number };
        lore_proposal_count?: number;
        agent_summaries?: Array<{ name: string; summary: string; confidence: number; needs_human_decision: boolean }>;
        generated_at?: string;
      }
    | undefined;

  if (!log) {
    return (
      <EmptyState
        title="Decision log unavailable"
        description="Decision log is available for runs that have completed. Run a pipeline to see the decision log."
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border p-3">
        <p className="text-sm font-medium">Run ID</p>
        <p className="font-mono text-xs text-muted-foreground">{log.run_id}</p>
      </div>
      <div className="rounded-md border p-3">
        <p className="text-sm font-medium">Scope</p>
        <p className="text-sm text-muted-foreground">{log.scope}</p>
      </div>
      <div className="rounded-md border p-3">
        <p className="text-sm font-medium">Gate</p>
        <p className="text-sm text-muted-foreground">
          {log.gate?.status ?? "—"} — {log.gate?.message ?? ""}
        </p>
      </div>
      {log.analysis_counts && (
        <div className="rounded-md border p-3">
          <p className="text-sm font-medium">Analysis counts</p>
          <p className="text-sm text-muted-foreground">
            {log.analysis_counts.total_findings} total (hard: {log.analysis_counts.hard_findings}, soft: {log.analysis_counts.soft_findings})
          </p>
        </div>
      )}
      {log.lore_proposal_count != null && (
        <div className="rounded-md border p-3">
          <p className="text-sm font-medium">Lore proposals</p>
          <p className="text-sm text-muted-foreground">{log.lore_proposal_count}</p>
        </div>
      )}
      {log.agent_summaries && log.agent_summaries.length > 0 && (
        <div className="rounded-md border p-3">
          <p className="text-sm font-medium">Agents</p>
          <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
            {log.agent_summaries.map((a) => (
              <li key={a.name}>{a.name}: {a.summary}</li>
            ))}
          </ul>
        </div>
      )}
      {log.generated_at && (
        <p className="text-xs text-muted-foreground">
          Generated: {log.generated_at}
        </p>
      )}
    </div>
  );
}
