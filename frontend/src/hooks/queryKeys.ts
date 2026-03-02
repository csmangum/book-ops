export const queryKeys = {
  version: ["version"] as const,
  indexStatus: ["index-status"] as const,
  chapterCatalog: ["chapter-catalog"] as const,
  issues: (filters?: Record<string, unknown>) => ["issues", filters] as const,
  chapterArtifact: (chapterId: number, artifactType: string) =>
    ["chapter-artifact", chapterId, artifactType] as const,
  projectArtifact: (artifactType: string) =>
    ["project-artifact", artifactType] as const,
  runHistory: ["run-history"] as const,
};
