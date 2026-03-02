import Link from "next/link";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, GateBadge } from "@/components/shared";
import type { RunHistoryEntry } from "@/lib/run-history";

export function RecentRunsList({ runs }: { runs: RunHistoryEntry[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Runs</CardTitle>
      </CardHeader>
      <CardContent>
        {runs.length === 0 ? (
          <EmptyState
            title="No run history yet"
            description="Run a chapter or project pipeline to create local run history."
          />
        ) : (
          <ul className="space-y-2">
            {runs.slice(0, 5).map((run) => (
              <li key={run.id} className="rounded-md border p-3">
                <div className="flex items-center justify-between gap-2">
                  <Link href={`/runs/${run.id}`} className="text-sm font-medium hover:underline">
                    {run.scope === "chapter"
                      ? `Chapter ${run.chapterId} pipeline`
                      : "Project pipeline"}
                  </Link>
                  <GateBadge gate={run.gate} />
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {new Date(run.createdAt).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
