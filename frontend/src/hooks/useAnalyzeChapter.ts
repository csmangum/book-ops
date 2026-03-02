"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type AnalyzeChapterRequest = ApiComponents["schemas"]["AnalyzeChapterRequest"];

export function useAnalyzeChapter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body: AnalyzeChapterRequest) => {
      const response = await apiClient.analyzeChapter(body);
      return unwrapEnvelope(response.data, "Could not analyze chapter.");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issues() });
    },
  });
}
