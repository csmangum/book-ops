"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiRunsListData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useRunsList() {
  return useQuery({
    queryKey: queryKeys.runs,
    queryFn: async () => {
      const response = await apiClient.listRuns();
      return unwrapEnvelope<ApiRunsListData>(response.data, "Could not load run history.");
    },
  });
}
