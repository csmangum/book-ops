export const queryKeys = {
  version: ["version"] as const,
  indexStatus: ["index-status"] as const,
  chapterCatalog: ["chapter-catalog"] as const,
  chapterContent: (chapterId: number) => ["chapter-content", chapterId] as const,
  issues: (filters?: Record<string, unknown>) => ["issues", filters] as const,
  runs: ["runs"] as const,
  run: (runId: string) => ["run", runId] as const,
  canonGraph: ["canon-graph"] as const,
  rules: ["rules"] as const,
  settings: ["settings"] as const,
  chapterArtifact: (chapterId: number, artifactType: string) =>
    ["chapter-artifact", chapterId, artifactType] as const,
  projectArtifact: (artifactType: string) =>
    ["project-artifact", artifactType] as const,
  runHistory: ["run-history"] as const,
};
