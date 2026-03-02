"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { toChapterRecords } from "@/lib/chapters";

export function useChapterCatalog() {
  return useQuery({
    queryKey: queryKeys.chapterCatalog,
    queryFn: async () => {
      const response = await apiClient.rebuildIndex();
      const data = unwrapEnvelope(
        response.data,
        "Could not rebuild index for chapter catalog.",
      );

      return toChapterRecords(data.symbolic);
    },
  });
}
