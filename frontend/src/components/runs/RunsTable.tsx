import Link from "next/link";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { GateBadge } from "@/components/shared/GateBadge";
import type { RunHistoryEntry } from "@/lib/run-history";

export function RunsTable({ runs }: { runs: RunHistoryEntry[] }) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Run ID</TableHead>
            <TableHead>Scope</TableHead>
            <TableHead>Gate</TableHead>
            <TableHead>Timestamp</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {runs.map((run) => (
            <TableRow key={run.id}>
              <TableCell className="font-mono text-xs">
                <Link href={`/runs/${run.id}`} className="hover:underline">
                  {run.id}
                </Link>
              </TableCell>
              <TableCell>
                {run.scope === "chapter"
                  ? `chapter:${run.chapterId ?? "?"}`
                  : "project"}
              </TableCell>
              <TableCell>
                <GateBadge gate={run.gate} />
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {new Date(run.createdAt).toLocaleString()}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
