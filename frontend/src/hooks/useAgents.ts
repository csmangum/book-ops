"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useAgents() {
  return useQuery({
    queryKey: queryKeys.agents(),
    queryFn: async () => {
      const response = await apiClient.listAgents();
      return unwrapEnvelope<Record<string, string>>(
        response.data,
        "Could not load agents.",
      );
    },
  });
}
