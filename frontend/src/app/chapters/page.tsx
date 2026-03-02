"use client";

import { useMemo, useState } from "react";

import { ChapterFilters, ChapterTable, type ChapterFilterState } from "@/components/chapters";
import { ErrorBanner, LoadingState } from "@/components/shared";
import { useAnalyzeChapter, useChapterCatalog, useProjectArtifact } from "@/hooks";
import type { ChapterTableRow } from "@/components/chapters/ChapterTable";
import { asArray, asRecord } from "@/lib/guards";

const defaultFilters: ChapterFilterState = {
  gate: "all",
  severity: "all",
  changed: "all",
};

export default function ChaptersPage() {
  const chapters = useChapterCatalog();
  const openIssues = useProjectArtifact("open-issues");
  const analyzeChapter = useAnalyzeChapter();
  const [filters, setFilters] = useState<ChapterFilterState>(defaultFilters);

  const chapterRows = useMemo<ChapterTableRow[]>(() => {
    const base = chapters.data ?? [];
    const issueList = asArray<{ scope?: string; severity?: string }>(
      asRecord(openIssues.data)?.issues,
    );

    return base.map((chapter) => {
      const issuesForChapter = issueList.filter(
        (issue) => issue.scope === `chapter:${chapter.chapterId}`,
      );
      return {
        ...chapter,
        gate: "pass_with_waivers",
        criticalCount: issuesForChapter.filter((issue) => issue.severity === "critical").length,
        highCount: issuesForChapter.filter((issue) => issue.severity === "high").length,
      };
    });
  }, [chapters.data, openIssues.data]);

  const filteredRows = useMemo(() => {
    const latestModifiedAt = chapterRows.reduce(
      (max, row) => Math.max(max, row.modifiedAt),
      0,
    );
    const recencyThreshold = latestModifiedAt - 7 * 24 * 60 * 60;

    return chapterRows.filter((row) => {
      if (filters.changed === "recent") {
        if (row.modifiedAt < recencyThreshold) {
          return false;
        }
      }

      if (filters.severity === "critical" && (row.criticalCount ?? 0) === 0) {
        return false;
      }
      if (filters.severity === "high" && (row.highCount ?? 0) === 0) {
        return false;
      }

      if (filters.gate !== "all" && row.gate !== filters.gate) {
        return false;
      }

      return true;
    });
  }, [chapterRows, filters]);

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Chapters</h2>
        <p className="text-sm text-muted-foreground">
          Chapter table derived from symbolic index data.
        </p>
      </section>

      <ChapterFilters value={filters} onChange={setFilters} />

      {chapters.isLoading ? <LoadingState label="Loading chapter catalog..." /> : null}
      {chapters.error ? <ErrorBanner error={chapters.error} /> : null}

      <ChapterTable
        chapters={filteredRows}
        onBulkAnalyze={(chapterIds) => {
          chapterIds.forEach((chapterId) => {
            analyzeChapter.mutate({
              chapter_id: chapterId,
              checks: ["tense", "invariants", "repetition", "motifs", "voice"],
            });
          });
        }}
      />
    </div>
  );
}
