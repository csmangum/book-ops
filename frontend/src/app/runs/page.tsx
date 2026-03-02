"use client";

import { EmptyState } from "@/components/shared";
import { RunsTable } from "@/components/runs";
import { useRunHistory } from "@/hooks";

export default function RunsPage() {
  const runHistory = useRunHistory();
  const runs = runHistory.data ?? [];

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Runs</h2>
        <p className="text-sm text-muted-foreground">
          Run history is currently sourced from local pipeline activity.
        </p>
      </section>

      {runs.length === 0 ? (
        <EmptyState
          title="No runs available"
          description="Backend does not currently expose run listing endpoints. Trigger a pipeline run to populate local history."
        />
      ) : (
        <RunsTable runs={runs} />
      )}
    </div>
  );
}
