"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiCanonGraphData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useCanonGraph() {
  return useQuery({
    queryKey: queryKeys.canonGraph,
    queryFn: async () => {
      const response = await apiClient.getCanonGraph();
      return unwrapEnvelope<ApiCanonGraphData>(
        response.data,
        "Could not load canon graph data.",
      );
    },
  });
}
