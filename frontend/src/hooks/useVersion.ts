"use client";

import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { queryKeys } from "@/hooks/queryKeys";

export function useVersion() {
  return useQuery({
    queryKey: queryKeys.version,
    queryFn: async () => {
      const response = await apiClient.getVersion();
      return unwrapEnvelope(response.data, "Could not load version metadata.");
    },
  });
}
