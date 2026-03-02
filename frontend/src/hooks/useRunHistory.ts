"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { readRunHistory } from "@/lib/run-history";

export function useRunHistory() {
  return useQuery({
    queryKey: queryKeys.runHistory,
    queryFn: async () => readRunHistory(),
    initialData: [],
    staleTime: Number.POSITIVE_INFINITY,
  });
}
