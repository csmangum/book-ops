"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiIndexStatusData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { toChapterRecords } from "@/lib/chapters";

export function useChapterCatalog() {
  return useQuery({
    queryKey: queryKeys.indexStatus,
    queryFn: async () => {
      const response = await apiClient.getIndexStatus(true);
      return unwrapEnvelope<ApiIndexStatusData>(
        response.data,
        "Could not load chapter catalog from index.",
      );
    },
    select: (data) => toChapterRecords(data.symbolic ?? []),
  });
}
