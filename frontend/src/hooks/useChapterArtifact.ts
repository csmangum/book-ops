"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export type ChapterArtifactType =
  | "analysis"
  | "gate"
  | "decision-log"
  | "continuity"
  | "style-audit"
  | "lore-delta"
  | "agent-results";

async function fetchChapterArtifact(chapterId: number, artifactType: ChapterArtifactType) {
  switch (artifactType) {
    case "analysis":
      return unwrapEnvelope(
        (await apiClient.getChapterAnalysisArtifact(chapterId)).data,
        "Could not load chapter analysis artifact.",
      );
    case "gate":
      return unwrapEnvelope(
        (await apiClient.getChapterGateArtifact(chapterId)).data,
        "Could not load chapter gate artifact.",
      );
    case "decision-log":
      return unwrapEnvelope(
        (await apiClient.getChapterDecisionLogArtifact(chapterId)).data,
        "Could not load chapter decision log artifact.",
      );
    case "continuity":
      return unwrapEnvelope(
        (await apiClient.getChapterContinuityArtifact(chapterId)).data,
        "Could not load chapter continuity artifact.",
      );
    case "style-audit":
      return unwrapEnvelope(
        (await apiClient.getChapterStyleAuditArtifact(chapterId)).data,
        "Could not load chapter style audit artifact.",
      );
    case "lore-delta":
      return unwrapEnvelope(
        (await apiClient.getChapterLoreDeltaArtifact(chapterId)).data,
        "Could not load chapter lore-delta artifact.",
      );
    case "agent-results":
      return unwrapEnvelope(
        (await apiClient.getChapterAgentResultsArtifact(chapterId)).data,
        "Could not load chapter agent-results artifact.",
      );
    default:
      return {};
  }
}

export function useChapterArtifact(
  chapterId: number,
  artifactType: ChapterArtifactType,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: queryKeys.chapterArtifact(chapterId, artifactType),
    queryFn: async () => fetchChapterArtifact(chapterId, artifactType),
    enabled: options?.enabled ?? Number.isFinite(chapterId),
  });
}
