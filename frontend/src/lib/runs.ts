import type { ApiRunEntry } from "@/lib/api";
import type { RunHistoryEntry } from "@/lib/run-history";

export function runHistoryFromApi(entry: ApiRunEntry): RunHistoryEntry {
  return {
    id: entry.run_id,
    scope: entry.scope.startsWith("chapter:") ? "chapter" : "project",
    chapterId: chapterIdFromScope(entry.scope),
    gate: entry.gate,
    createdAt: entry.created_at,
  };
}

function chapterIdFromScope(scope: string) {
  if (!scope.startsWith("chapter:")) {
    return undefined;
  }
  const id = Number(scope.split(":")[1]);
  return Number.isFinite(id) ? id : undefined;
}
