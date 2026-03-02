"use client";

import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { queryKeys } from "@/hooks/queryKeys";

export function useIndexStatus() {
  return useQuery({
    queryKey: queryKeys.indexStatus,
    queryFn: async () => {
      const response = await apiClient.getIndexStatus(true);
      return unwrapEnvelope(response.data, "Could not load index status.");
    },
  });
}
