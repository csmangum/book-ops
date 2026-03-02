"use client";

import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAnalyzeChapter, useAnalyzeProject, usePipelineRun, useReportOpen } from "@/hooks";
import type { ChapterRecord } from "@/lib/chapters";

export function QuickActions({ chapters }: { chapters: ChapterRecord[] }) {
  const [chapterId, setChapterId] = useState<string>(
    chapters[0] ? String(chapters[0].chapterId) : "",
  );
  const [latestReportPath, setLatestReportPath] = useState<string>("");

  const analyzeChapter = useAnalyzeChapter();
  const analyzeProject = useAnalyzeProject();
  const runPipeline = usePipelineRun();
  const openReport = useReportOpen();

  const hasChapter = useMemo(() => Number.isFinite(Number(chapterId)), [chapterId]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2">
          <Label htmlFor="quick-chapter-id">Chapter ID</Label>
          <Input
            id="quick-chapter-id"
            value={chapterId}
            onChange={(event) => setChapterId(event.target.value)}
            placeholder="14"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            disabled={!hasChapter || analyzeChapter.isPending}
            onClick={() =>
              analyzeChapter.mutate({
                chapter_id: Number(chapterId),
                checks: ["tense", "invariants", "repetition", "motifs", "voice"],
              })
            }
          >
            Analyze chapter
          </Button>
          <Button
            variant="outline"
            disabled={analyzeProject.isPending}
            onClick={() => analyzeProject.mutate({})}
          >
            Analyze project
          </Button>
          <Button
            variant="outline"
            disabled={!hasChapter || runPipeline.isPending}
            onClick={() =>
              runPipeline.mutate({
                scope: "chapter",
                body: { chapter_id: Number(chapterId), strict: false },
              })
            }
          >
            Run chapter pipeline
          </Button>
          <Button
            variant="outline"
            disabled={runPipeline.isPending}
            onClick={() =>
              runPipeline.mutate({
                scope: "project",
                body: { strict: false },
              })
            }
          >
            Run project pipeline
          </Button>
          <Button
            disabled={openReport.isPending}
            onClick={async () => {
              const result = await openReport.mutateAsync({
                scope: "project",
              });
              setLatestReportPath(result.path);
            }}
          >
            Open latest report
          </Button>
        </div>
        {latestReportPath ? (
          <p className="text-sm text-muted-foreground">Latest report path: {latestReportPath}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}
