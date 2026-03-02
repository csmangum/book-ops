"use client";

import {
  ChangedSinceLastRun,
  GateStatusCards,
  QuickActions,
  RecentRunsList,
  type Blocker,
  TopBlockersList,
} from "@/components/home";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorBanner, LoadingState } from "@/components/shared";
import {
  useChapterArtifact,
  useChapterCatalog,
  useIndexStatus,
  useProjectArtifact,
  useRunHistory,
} from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

export default function HomePage() {
  const chapters = useChapterCatalog();
  const indexStatus = useIndexStatus();
  const sampleChapterId = chapters.data?.[0]?.chapterId ?? 1;
  const runHistory = useRunHistory();
  const projectGate = useProjectArtifact("gate");
  const openIssues = useProjectArtifact("open-issues");
  const chapterGate = useChapterArtifact(sampleChapterId, "gate");

  const openIssueRecords = asArray<Blocker>(asRecord(openIssues.data)?.issues);
  const blockerIssues = openIssueRecords.filter((issue) =>
    ["critical", "high"].includes(issue.severity ?? ""),
  );

  return (
    <div className="space-y-4">
      <section className="space-y-1">
        <h2 className="text-xl font-semibold">Command Center</h2>
        <p className="text-sm text-muted-foreground">
          Operational snapshot across gates, blockers, and pipeline actions.
        </p>
      </section>

      {chapters.isLoading ? <LoadingState label="Loading chapter catalog..." /> : null}
      {chapters.error ? <ErrorBanner error={chapters.error} /> : null}
      {indexStatus.error ? (
        <ErrorBanner error={indexStatus.error} title="Index status unavailable" />
      ) : null}
      {projectGate.error ? <ErrorBanner error={projectGate.error} title="Project gate unavailable" /> : null}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Index Status</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          {indexStatus.data ? (
            <p>
              Files indexed:{" "}
              {String(asRecord(indexStatus.data)?.file_count ?? "unknown")} ·
              Symbolic:{" "}
              {String(asRecord(indexStatus.data)?.symbolic_exists ?? false)} ·
              Semantic:{" "}
              {String(asRecord(indexStatus.data)?.semantic_exists ?? false)}
            </p>
          ) : (
            <p>Index metadata has not been loaded yet.</p>
          )}
        </CardContent>
      </Card>

      <GateStatusCards
        projectGate={asRecord(projectGate.data)}
        chapterGate={asRecord(chapterGate.data)}
      />

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2 space-y-4">
          <TopBlockersList blockers={blockerIssues} />
          <ChangedSinceLastRun chapters={chapters.data ?? []} />
        </div>
        <div className="space-y-4">
          <RecentRunsList runs={runHistory.data ?? []} />
          <QuickActions chapters={chapters.data ?? []} />
        </div>
      </div>
    </div>
  );
}
