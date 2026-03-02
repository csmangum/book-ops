"use client";

import { useMemo, useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { ErrorBanner, LoadingState } from "@/components/shared";
import { usePatchSettings, useSettings } from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

export default function SettingsPage() {
  const settingsQuery = useSettings();
  const patchSettings = usePatchSettings();
  const [chaptersDirDraft, setChaptersDirDraft] = useState<string | null>(null);
  const [loreDirDraft, setLoreDirDraft] = useState<string | null>(null);
  const [excludedDirsDraft, setExcludedDirsDraft] = useState<string | null>(null);
  const [reviewerHandle, setReviewerHandle] = useState("bookops-ui");
  const [providerToggles, setProviderToggles] = useState(
    "developmental_editor=true\ncontinuity_guardian=true",
  );

  const loadedValues = useMemo(() => {
    const project = asRecord(settingsQuery.data?.project);
    const paths = asRecord(settingsQuery.data?.paths);
    const excluded = asArray<string>(paths?.excluded_dirs);
    return {
      chaptersDir: String(project?.chapters_dir ?? "chapters"),
      loreDir: String(project?.lore_dir ?? "lore"),
      excludedDirs:
        excluded.length > 0 ? excluded.join("\n") : ".bookops\nreports\n.git",
    };
  }, [settingsQuery.data]);

  const chaptersDir = chaptersDirDraft ?? loadedValues.chaptersDir;
  const loreDir = loreDirDraft ?? loadedValues.loreDir;
  const excludedDirs = excludedDirsDraft ?? loadedValues.excludedDirs;

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Settings</h2>
        <p className="text-sm text-muted-foreground">
          Runtime settings loaded from backend and patchable from this form.
        </p>
      </section>

      {settingsQuery.isLoading ? <LoadingState label="Loading settings..." /> : null}
      {settingsQuery.error ? <ErrorBanner error={settingsQuery.error} /> : null}
      {patchSettings.error ? (
        <ErrorBanner error={patchSettings.error} title="Failed to update settings" />
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project paths</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label>Chapters dir</Label>
              <Input
                value={chaptersDir}
                onChange={(event) => setChaptersDirDraft(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Lore dir</Label>
              <Input
                value={loreDir}
                onChange={(event) => setLoreDirDraft(event.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label>Excluded dirs</Label>
              <Textarea
                value={excludedDirs}
                onChange={(event) => setExcludedDirsDraft(event.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Reviewer defaults</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label>Reviewer handle</Label>
              <Input value={reviewerHandle} onChange={(event) => setReviewerHandle(event.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Provider toggles</Label>
              <Textarea value={providerToggles} onChange={(event) => setProviderToggles(event.target.value)} />
            </div>
            <Button
              variant="outline"
              disabled={patchSettings.isPending}
              onClick={() =>
                patchSettings.mutate({
                  project: {
                    chapters_dir: chaptersDir.trim(),
                    lore_dir: loreDir.trim(),
                  },
                  paths: {
                    excluded_dirs: excludedDirs
                      .split("\n")
                      .map((item) => item.trim())
                      .filter(Boolean),
                  },
                  reviewer_defaults: {
                    handle: reviewerHandle.trim(),
                    provider_toggles: providerToggles
                      .split("\n")
                      .map((item) => item.trim())
                      .filter(Boolean),
                  },
                })
              }
            >
              {patchSettings.isPending ? "Saving..." : "Save settings"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
