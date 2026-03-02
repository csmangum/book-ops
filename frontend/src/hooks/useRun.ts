"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiRunEntry } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useRun(runId: string) {
  return useQuery({
    queryKey: queryKeys.run(runId),
    queryFn: async () => {
      const response = await apiClient.getRun(runId);
      return unwrapEnvelope<ApiRunEntry>(response.data, "Could not load run.");
    },
    enabled: runId.length > 0,
  });
}
