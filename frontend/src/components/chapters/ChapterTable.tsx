"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Checkbox } from "@/components/ui/checkbox";
import { EmptyState, GateBadge } from "@/components/shared";
import type { ChapterRecord } from "@/lib/chapters";

export type ChapterTableRow = ChapterRecord & {
  gate?: string;
  highCount?: number;
  criticalCount?: number;
};

export function ChapterTable({
  chapters,
  onBulkAnalyze,
}: {
  chapters: ChapterTableRow[];
  onBulkAnalyze: (chapterIds: number[]) => void;
}) {
  const [selected, setSelected] = useState<Record<number, boolean>>({});

  const selectedIds = useMemo(
    () =>
      Object.entries(selected)
        .filter((entry) => entry[1])
        .map((entry) => Number(entry[0])),
    [selected],
  );

  if (chapters.length === 0) {
    return <EmptyState title="No chapters found" description="Rebuild index to populate chapters table." />;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{chapters.length} chapters</p>
        <Button
          variant="outline"
          size="sm"
          disabled={selectedIds.length === 0}
          onClick={() => onBulkAnalyze(selectedIds)}
        >
          Bulk analyze selected ({selectedIds.length})
        </Button>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-10" />
              <TableHead>Chapter</TableHead>
              <TableHead>Last edited</TableHead>
              <TableHead>Gate</TableHead>
              <TableHead>Critical / High</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {chapters.map((chapter) => (
              <TableRow key={chapter.path}>
                <TableCell>
                  <Checkbox
                    checked={Boolean(selected[chapter.chapterId])}
                    onCheckedChange={(checked) =>
                      setSelected((current) => ({
                        ...current,
                        [chapter.chapterId]: Boolean(checked),
                      }))
                    }
                  />
                </TableCell>
                <TableCell>
                  <Link
                    href={`/chapters/${chapter.chapterId}`}
                    className="font-medium hover:underline"
                  >
                    {chapter.chapterId}. {chapter.title}
                  </Link>
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {new Date(chapter.modifiedAt * 1000).toLocaleString()}
                </TableCell>
                <TableCell>
                  <GateBadge gate={chapter.gate ?? "pass_with_waivers"} />
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {chapter.criticalCount ?? 0} / {chapter.highCount ?? 0}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
