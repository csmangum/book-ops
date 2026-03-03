"use client";

import { useMemo } from "react";
import { useParams } from "next/navigation";

import {
  DecisionLogViewer,
  RunAgentResultsTab,
  RunArtifactsTab,
  RunFindingsTab,
  RunGateTab,
  RunSummary,
} from "@/components/runs";
import { EmptyState } from "@/components/shared";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useRun, useRunHistory } from "@/hooks";
import { runHistoryFromApi } from "@/lib/runs";

export default function RunDetailPage() {
  const params = useParams<{ runId: string }>();
  const runQuery = useRun(params.runId);
  const runHistory = useRunHistory();

  const run = useMemo(
    () =>
      runQuery.data
        ? runHistoryFromApi(runQuery.data)
        : (runHistory.data ?? []).find((item) => item.id === params.runId),
    [params.runId, runHistory.data, runQuery.data],
  );

  const runDetail = runQuery.data;

  if (!run) {
    return (
      <EmptyState
        title="Run not found"
        description="This run ID is not present in local run history."
      />
    );
  }

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Run Detail</h2>
        <p className="text-sm text-muted-foreground">
          Run detail from backend when available, with local fallback.
        </p>
      </section>
      <RunSummary run={run} />
      <Tabs defaultValue="findings">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="findings">Findings</TabsTrigger>
          <TabsTrigger value="gate">Gate</TabsTrigger>
          <TabsTrigger value="agents">Agents</TabsTrigger>
          <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
          <TabsTrigger value="decision-log">Decision log</TabsTrigger>
        </TabsList>
        <TabsContent value="findings" className="mt-4">
          <RunFindingsTab run={run} />
        </TabsContent>
        <TabsContent value="gate" className="mt-4">
          <RunGateTab run={run} />
        </TabsContent>
        <TabsContent value="agents" className="mt-4">
          <RunAgentResultsTab runDetail={runDetail} />
        </TabsContent>
        <TabsContent value="artifacts" className="mt-4">
          <RunArtifactsTab run={run} />
        </TabsContent>
        <TabsContent value="decision-log" className="mt-4">
          <DecisionLogViewer runDetail={runDetail} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
