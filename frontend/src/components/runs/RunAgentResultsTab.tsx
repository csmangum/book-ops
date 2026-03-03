"use client";

import { EmptyState } from "@/components/shared/EmptyState";

type AgentResult = {
  name: string;
  summary: string;
  findings: unknown[];
  proposals: unknown[];
  confidence: number;
  needs_human_decision: boolean;
};

export function RunAgentResultsTab({
  runDetail,
}: {
  runDetail?: Record<string, unknown> | null;
}) {
  const results = (runDetail?.agent_results as AgentResult[] | undefined) ?? [];

  if (results.length === 0) {
    return (
      <EmptyState
        title="No agent results"
        description="Agent results are available for chapter pipeline runs. Run a chapter pipeline to see agent outputs."
      />
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        {results.length} agent(s) ran in this pipeline.
      </p>
      <div className="space-y-3">
        {results.map((r) => (
          <div
            key={r.name}
            className="rounded-md border p-3"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="font-medium">{r.name.replace(/_/g, " ")}</p>
              <span className="text-xs text-muted-foreground">
                confidence: {(r.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">{r.summary}</p>
            {(r.findings?.length ?? 0) > 0 && (
              <p className="mt-1 text-xs text-muted-foreground">
                {r.findings.length} finding(s)
              </p>
            )}
            {(r.proposals?.length ?? 0) > 0 && (
              <p className="mt-1 text-xs text-muted-foreground">
                {r.proposals.length} proposal(s)
              </p>
            )}
            {r.needs_human_decision && (
              <p className="mt-1 text-xs font-medium text-amber-600">
                Needs human decision
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
