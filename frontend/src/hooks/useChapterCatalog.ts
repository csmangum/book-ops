"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiIndexStatusData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { toChapterRecords } from "@/lib/chapters";

export function useChapterCatalog() {
  return useQuery({
    queryKey: queryKeys.chapterCatalog,
    queryFn: async () => {
      const response = await apiClient.getIndexStatus();
      const data = unwrapEnvelope<ApiIndexStatusData>(
        response.data,
        "Could not load chapter catalog from index.",
      );

      return toChapterRecords(data.symbolic ?? []);
    },
  });
}
