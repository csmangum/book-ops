"use client";

import { FindingCard } from "@/components/chapters/FindingCard";
import { EmptyState } from "@/components/shared/EmptyState";
import { useChapterArtifact } from "@/hooks/useChapterArtifact";
import { useProjectArtifact } from "@/hooks/useProjectArtifact";
import { asArray, asRecord } from "@/lib/guards";
import type { RunHistoryEntry } from "@/lib/run-history";

export function RunFindingsTab({ run }: { run: RunHistoryEntry }) {
  const chapterId = run.chapterId;
  const isChapter = run.scope === "chapter" && chapterId != null;

  const analysisQuery = useChapterArtifact(chapterId ?? 0, "analysis", { enabled: isChapter });
  const openIssuesQuery = useProjectArtifact("open-issues", { enabled: !isChapter });

  const chapterFindings = asArray<Record<string, unknown>>(
    asRecord(analysisQuery.data)?.generated_findings ?? [],
  );
  const projectIssues = asArray<Record<string, unknown>>(
    asRecord(openIssuesQuery.data)?.issues ?? [],
  );

  const findings = isChapter ? chapterFindings : projectIssues;
  const isLoading = isChapter ? analysisQuery.isLoading : openIssuesQuery.isLoading;
  const isError = isChapter ? analysisQuery.isError : openIssuesQuery.isError;

  if (isLoading) {
    return (
      <p className="text-sm text-muted-foreground">Loading findings…</p>
    );
  }

  if (isError) {
    return (
      <EmptyState
        title="Could not load findings"
        description={
          isChapter
            ? "Analysis artifact may not exist yet. Run the chapter pipeline first."
            : "Open issues artifact may not exist yet. Run the project pipeline first."
        }
      />
    );
  }

  if (findings.length === 0) {
    return (
      <EmptyState
        title="No findings"
        description={
          isChapter
            ? "No findings for this chapter run."
            : "No open issues for this project run."
        }
      />
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted-foreground">
        {findings.length} finding(s) from this run.
      </p>
      {findings.map((item, index) => (
        <FindingCard
          key={`${item.rule_id ?? "f"}-${item.id ?? index}`}
          finding={item}
        />
      ))}
    </div>
  );
}
