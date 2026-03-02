"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiRulesData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useRules() {
  return useQuery({
    queryKey: queryKeys.rules,
    queryFn: async () => {
      const response = await apiClient.getRules();
      return unwrapEnvelope<ApiRulesData>(response.data, "Could not load rules.");
    },
  });
}
