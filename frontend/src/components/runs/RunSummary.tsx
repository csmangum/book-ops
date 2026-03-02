import type { RunHistoryEntry } from "@/lib/run-history";
import { GateBadge } from "@/components/shared/GateBadge";

export function RunSummary({ run }: { run: RunHistoryEntry }) {
  return (
    <div className="rounded-md border p-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold">{run.id}</p>
        <GateBadge gate={run.gate} />
      </div>
      <p className="mt-1 text-sm text-muted-foreground">
        Scope: {run.scope === "chapter" ? `chapter:${run.chapterId}` : "project"}
      </p>
      <p className="text-xs text-muted-foreground">
        Created: {new Date(run.createdAt).toLocaleString()}
      </p>
    </div>
  );
}
