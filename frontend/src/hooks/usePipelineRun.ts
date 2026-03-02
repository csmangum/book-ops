"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import {
  apiClient,
  type ApiComponents,
  type ApiPipelineData,
} from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { addRunHistoryEntry } from "@/lib/run-history";

type ChapterRequest = ApiComponents["schemas"]["PipelineChapterRequest"];
type ProjectRequest = ApiComponents["schemas"]["PipelineProjectRequest"];

type PipelineInput =
  | { scope: "chapter"; body: ChapterRequest }
  | { scope: "project"; body?: ProjectRequest };

export function usePipelineRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: PipelineInput) => {
      if (input.scope === "chapter") {
      const response = await apiClient.runChapterPipeline(input.body);
      const data = unwrapEnvelope<ApiPipelineData>(
        response.data,
        "Could not run chapter pipeline.",
      );
      addRunHistoryEntry({
        id: data.run_id ?? crypto.randomUUID(),
        scope: "chapter",
        chapterId: input.body.chapter_id,
        gate: data.gate,
        createdAt: new Date().toISOString(),
      });
      return data;
      }

      const response = await apiClient.runProjectPipeline(
        input.body ?? { strict: false },
      );
      const data = unwrapEnvelope<ApiPipelineData>(
        response.data,
        "Could not run project pipeline.",
      );
      addRunHistoryEntry({
        id: data.run_id ?? crypto.randomUUID(),
        scope: "project",
        gate: data.gate,
        createdAt: new Date().toISOString(),
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.runHistory });
      queryClient.invalidateQueries({ queryKey: queryKeys.runs });
      queryClient.invalidateQueries({ queryKey: queryKeys.issues() });
      queryClient.invalidateQueries({ queryKey: queryKeys.projectArtifact("gate") });
      queryClient.invalidateQueries({ queryKey: queryKeys.projectArtifact("open-issues") });
    },
  });
}
