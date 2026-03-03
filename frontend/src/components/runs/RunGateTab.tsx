"use client";

import { GateBadge } from "@/components/shared/GateBadge";
import { EmptyState } from "@/components/shared/EmptyState";
import { useChapterArtifact } from "@/hooks/useChapterArtifact";
import { useProjectArtifact } from "@/hooks/useProjectArtifact";
import type { RunHistoryEntry } from "@/lib/run-history";

function asArray<T>(v: unknown): T[] {
  if (Array.isArray(v)) return v as T[];
  return [];
}

function asRecord(v: unknown): Record<string, unknown> | null {
  if (v && typeof v === "object" && !Array.isArray(v)) return v as Record<string, unknown>;
  return null;
}

export function RunGateTab({ run }: { run: RunHistoryEntry }) {
  const chapterId = run.chapterId;
  const isChapter = run.scope === "chapter" && chapterId != null;

  const chapterGateQuery = useChapterArtifact(chapterId ?? 0, "gate", { enabled: isChapter });
  const projectGateQuery = useProjectArtifact("gate", { enabled: !isChapter });

  const gateData = isChapter ? chapterGateQuery.data : projectGateQuery.data;
  const isLoading = isChapter ? chapterGateQuery.isLoading : projectGateQuery.isLoading;
  const isError = isChapter ? chapterGateQuery.isError : projectGateQuery.isError;

  if (isLoading) {
    return (
      <p className="text-sm text-muted-foreground">Loading gate result…</p>
    );
  }

  if (isError || !gateData) {
    return (
      <EmptyState
        title="Could not load gate"
        description={
          isChapter
            ? "Gate artifact may not exist yet. Run the chapter pipeline first."
            : "Gate artifact may not exist yet. Run the project pipeline first."
        }
      />
    );
  }

  const gate = asRecord(gateData);
  const status = String(gate?.status ?? run.gate ?? "unknown");
  const message = String(gate?.message ?? "");
  const blockingIds = asArray<string>(gate?.blocking_issue_ids);
  const warningIds = asArray<string>(gate?.warning_issue_ids);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Status</span>
        <GateBadge gate={status} />
      </div>
      {message && (
        <p className="text-sm text-muted-foreground">{message}</p>
      )}
      {(blockingIds.length > 0 || warningIds.length > 0) && (
        <div className="space-y-2 rounded-md border p-3">
          {blockingIds.length > 0 && (
            <div>
              <p className="text-sm font-medium">Blocking issues</p>
              <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
                {blockingIds.map((id) => (
                  <li key={id}>{id}</li>
                ))}
              </ul>
            </div>
          )}
          {warningIds.length > 0 && (
            <div>
              <p className="text-sm font-medium">Warnings</p>
              <ul className="mt-1 list-inside list-disc text-sm text-muted-foreground">
                {warningIds.map((id) => (
                  <li key={id}>{id}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
