"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiChapterContentData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useChapterContent(chapterId: number) {
  return useQuery({
    queryKey: queryKeys.chapterContent(chapterId),
    queryFn: async () => {
      const response = await apiClient.getChapterContent(chapterId);
      return unwrapEnvelope<ApiChapterContentData>(
        response.data,
        "Could not load chapter content.",
      );
    },
    enabled: Number.isFinite(chapterId),
  });
}
