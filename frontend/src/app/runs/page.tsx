"use client";

import { EmptyState, ErrorBanner, LoadingState } from "@/components/shared";
import { RunsTable } from "@/components/runs";
import { useRunHistory, useRunsList } from "@/hooks";
import { runHistoryFromApi } from "@/lib/runs";

export default function RunsPage() {
  const runsQuery = useRunsList();
  const runHistory = useRunHistory();
  const apiRuns = runsQuery.data?.runs?.map(runHistoryFromApi) ?? [];
  const localRuns = runHistory.data ?? [];
  const runs = runsQuery.isSuccess ? apiRuns : localRuns;

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Runs</h2>
        <p className="text-sm text-muted-foreground">
          Run history from backend when available, with local fallback.
        </p>
      </section>

      {runsQuery.isLoading ? <LoadingState label="Loading runs..." /> : null}
      {runsQuery.error ? (
        <ErrorBanner
          error={runsQuery.error}
          title="Backend run history unavailable"
        />
      ) : null}

      {runs.length === 0 ? (
        <EmptyState
          title="No runs available"
          description="Trigger a pipeline run to populate history."
        />
      ) : (
        <RunsTable runs={runs} />
      )}
    </div>
  );
}
