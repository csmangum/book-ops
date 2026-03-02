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
import { useChapterArtifact, useChapterCatalog, useChapterContent } from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

export default function ChapterWorkbenchPage() {
  const params = useParams<{ chapterId: string }>();
  const chapterId = Number(params.chapterId);
  const [showDiff, setShowDiff] = useState(false);

  const chapters = useChapterCatalog();
  const chapterContent = useChapterContent(chapterId);
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
        "Diff endpoint is not available in current API contract.",
        "Showing diff placeholder scaffold.",
      ].join("\n");
    }

    const content = chapterContent.data?.content?.trim();
    if (content) {
      return content;
    }

    return [
      `# Chapter ${chapterId} manuscript placeholder`,
      "",
      "Chapter content endpoint returned no data.",
      "This placeholder is shown until manuscript content is available.",
    ].join("\n");
  }, [chapterContent.data?.content, chapterId, showDiff]);

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
      {chapterContent.error ? (
        <ErrorBanner error={chapterContent.error} title="Chapter content unavailable" />
      ) : null}

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
