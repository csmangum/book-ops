"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type AnalyzeProjectRequest = ApiComponents["schemas"]["AnalyzeProjectRequest"];

export function useAnalyzeProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body?: AnalyzeProjectRequest) => {
      const response = await apiClient.analyzeProject(body ?? {});
      return unwrapEnvelope(response.data, "Could not analyze project.");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issues() });
    },
  });
}
