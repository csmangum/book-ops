"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export type ProjectArtifactType =
  | "gate"
  | "open-issues"
  | "resolved-issues"
  | "timeline"
  | "motifs";

async function fetchProjectArtifact(artifactType: ProjectArtifactType) {
  switch (artifactType) {
    case "gate":
      return unwrapEnvelope(
        (await apiClient.getProjectGateArtifact()).data,
        "Could not load project gate artifact.",
      );
    case "open-issues":
      return unwrapEnvelope(
        (await apiClient.getProjectOpenIssuesArtifact()).data,
        "Could not load project open issues artifact.",
      );
    case "resolved-issues":
      return unwrapEnvelope(
        (await apiClient.getProjectResolvedIssuesArtifact()).data,
        "Could not load project resolved issues artifact.",
      );
    case "timeline":
      return unwrapEnvelope(
        (await apiClient.getProjectTimelineArtifact()).data,
        "Could not load project timeline artifact.",
      );
    case "motifs":
      return unwrapEnvelope(
        (await apiClient.getProjectMotifsArtifact()).data,
        "Could not load project motif artifact.",
      );
    default:
      return {};
  }
}

export function useProjectArtifact(artifactType: ProjectArtifactType) {
  return useQuery({
    queryKey: queryKeys.projectArtifact(artifactType),
    queryFn: async () => fetchProjectArtifact(artifactType),
  });
}
