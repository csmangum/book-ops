"use client";

import {
  ChangedSinceLastRun,
  GateStatusCards,
  QuickActions,
  RecentRunsList,
  TopBlockersList,
} from "@/components/home";
import { ErrorBanner, LoadingState } from "@/components/shared";
import {
  useChapterArtifact,
  useChapterCatalog,
  useProjectArtifact,
  useRunHistory,
} from "@/hooks";

export default function HomePage() {
  const chapters = useChapterCatalog();
  const sampleChapterId = chapters.data?.[0]?.chapterId ?? 1;
  const runHistory = useRunHistory();
  const projectGate = useProjectArtifact("gate");
  const openIssues = useProjectArtifact("open-issues");
  const chapterGate = useChapterArtifact(sampleChapterId, "gate");

  const blockerIssues = Array.isArray((openIssues.data as { issues?: unknown[] } | undefined)?.issues)
    ? ((openIssues.data as { issues: { severity?: string }[] }).issues ?? []).filter((issue) =>
        ["critical", "high"].includes(issue.severity ?? ""),
      )
    : [];

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
      {projectGate.error ? <ErrorBanner error={projectGate.error} title="Project gate unavailable" /> : null}

      <GateStatusCards
        projectGate={projectGate.data as Record<string, unknown> | undefined}
        chapterGate={chapterGate.data as Record<string, unknown> | undefined}
      />

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2 space-y-4">
          <TopBlockersList blockers={blockerIssues as never[]} />
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
