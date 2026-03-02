"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";

import {
  ChapterNavigator,
  FindingsPanel,
  ManuscriptDiffToggle,
  ManuscriptEditor,
} from "@/components/chapters";
import { ErrorBanner, LoadingState } from "@/components/shared";
import { useChapterArtifact, useChapterCatalog } from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

export default function ChapterWorkbenchPage() {
  const params = useParams<{ chapterId: string }>();
  const chapterId = Number(params.chapterId);
  const [showDiff, setShowDiff] = useState(false);

  const chapters = useChapterCatalog();
  const analysis = useChapterArtifact(chapterId, "analysis");
  const continuity = useChapterArtifact(chapterId, "continuity");
  const styleAudit = useChapterArtifact(chapterId, "style-audit");
  const loreDelta = useChapterArtifact(chapterId, "lore-delta");

  const analysisFindings = asArray<Record<string, unknown>>(
    asRecord(analysis.data)?.generated_findings,
  );
  const continuityFindings = asArray<Record<string, unknown>>(
    asRecord(continuity.data)?.findings,
  );
  const styleFindings = asArray<Record<string, unknown>>(
    asRecord(styleAudit.data)?.findings,
  );
  const loreProposals = asArray<Record<string, unknown>>(
    asRecord(loreDelta.data)?.proposals,
  );

  const manuscriptText = useMemo(() => {
    if (showDiff) {
      return [
        "# Diff view placeholder",
        "",
        "No chapter content endpoint exists in current API contract.",
        "Use this placeholder to validate workbench layout and Monaco diagnostics scaffolding.",
      ].join("\n");
    }

    return [
      `# Chapter ${chapterId} manuscript placeholder`,
      "",
      "Chapter file read API is not currently available.",
      "Once backend provides manuscript content, this panel will load real chapter text.",
    ].join("\n");
  }, [chapterId, showDiff]);

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Chapter Workbench</h2>
        <p className="text-sm text-muted-foreground">
          Three-pane review with manuscript editor and findings.
        </p>
      </section>

      {analysis.isLoading ? <LoadingState label="Loading chapter artifacts..." /> : null}
      {analysis.error ? <ErrorBanner error={analysis.error} /> : null}

      <div className="grid gap-4 lg:grid-cols-[220px_1fr_420px]">
        <div className="space-y-3">
          <h3 className="text-sm font-semibold">Chapter navigator</h3>
          <ChapterNavigator
            chapters={chapters.data ?? []}
            activeChapterId={chapterId}
          />
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Manuscript</h3>
            <ManuscriptDiffToggle
              showDiff={showDiff}
              onToggle={() => setShowDiff((current) => !current)}
            />
          </div>
          <ManuscriptEditor value={manuscriptText} readOnly />
        </div>
        <div className="space-y-3">
          <h3 className="text-sm font-semibold">Findings</h3>
          <FindingsPanel
            continuityFindings={continuityFindings}
            styleFindings={styleFindings}
            analysisFindings={analysisFindings}
            loreProposals={loreProposals}
          />
        </div>
      </div>
    </div>
  );
}
