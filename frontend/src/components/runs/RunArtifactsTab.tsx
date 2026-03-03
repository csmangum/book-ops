"use client";

import { EmptyState } from "@/components/shared/EmptyState";
import { useChapterArtifact, type ChapterArtifactType } from "@/hooks/useChapterArtifact";
import { useProjectArtifact, type ProjectArtifactType } from "@/hooks/useProjectArtifact";
import type { RunHistoryEntry } from "@/lib/run-history";

const CHAPTER_ARTIFACTS: { type: ChapterArtifactType; label: string }[] = [
  { type: "analysis", label: "Analysis" },
  { type: "gate", label: "Gate" },
  { type: "decision-log", label: "Decision log" },
  { type: "agent-results", label: "Agent results" },
];

const PROJECT_ARTIFACTS: { type: ProjectArtifactType; label: string }[] = [
  { type: "gate", label: "Gate" },
  { type: "open-issues", label: "Open issues" },
  { type: "timeline", label: "Timeline" },
  { type: "motifs", label: "Motifs" },
];

export function RunArtifactsTab({ run }: { run: RunHistoryEntry }) {
  const chapterId = run.chapterId;
  const isChapter = run.scope === "chapter" && chapterId != null;

  if (!isChapter && run.scope !== "project") {
    return (
      <EmptyState
        title="Unknown scope"
        description="Run scope could not be determined."
      />
    );
  }

  if (isChapter) {
    return (
      <ChapterArtifactsList chapterId={chapterId!} />
    );
  }

  return <ProjectArtifactsList />;
}

function ChapterArtifactsList({ chapterId }: { chapterId: number }) {
  return (
    <div className="space-y-2">
      <p className="text-sm text-muted-foreground">
        Artifacts for chapter {chapterId}:
      </p>
      <ul className="space-y-2">
        {CHAPTER_ARTIFACTS.map(({ type, label }) => (
          <ChapterArtifactItem key={type} chapterId={chapterId} type={type} label={label} />
        ))}
      </ul>
    </div>
  );
}

function ChapterArtifactItem({
  chapterId,
  type,
  label,
}: {
  chapterId: number;
  type: ChapterArtifactType;
  label: string;
}) {
  const query = useChapterArtifact(chapterId, type);
  const status = query.isLoading ? "loading" : query.isError ? "unavailable" : "available";

  return (
    <li className="flex items-center justify-between rounded-md border p-2">
      <span className="text-sm font-medium">{label}</span>
      <span
        className={`text-xs ${
          status === "available"
            ? "text-emerald-600"
            : status === "loading"
              ? "text-muted-foreground"
              : "text-muted-foreground"
        }`}
      >
        {status === "loading" ? "Loading…" : status === "available" ? "Available" : "—"}
      </span>
    </li>
  );
}

function ProjectArtifactsList() {
  return (
    <div className="space-y-2">
      <p className="text-sm text-muted-foreground">
        Artifacts for project run:
      </p>
      <ul className="space-y-2">
        {PROJECT_ARTIFACTS.map(({ type, label }) => (
          <ProjectArtifactItem key={type} type={type} label={label} />
        ))}
      </ul>
    </div>
  );
}

function ProjectArtifactItem({
  type,
  label,
}: {
  type: ProjectArtifactType;
  label: string;
}) {
  const query = useProjectArtifact(type);
  const status = query.isLoading ? "loading" : query.isError ? "unavailable" : "available";

  return (
    <li className="flex items-center justify-between rounded-md border p-2">
      <span className="text-sm font-medium">{label}</span>
      <span
        className={`text-xs ${
          status === "available"
            ? "text-emerald-600"
            : status === "loading"
              ? "text-muted-foreground"
              : "text-muted-foreground"
        }`}
      >
        {status === "loading" ? "Loading…" : status === "available" ? "Available" : "—"}
      </span>
    </li>
  );
}
