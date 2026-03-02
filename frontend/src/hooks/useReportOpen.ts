"use client";

import { useMutation } from "@tanstack/react-query";

import { apiClient, type ApiReportOpenData } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type ReportOpenInput = {
  scope: "chapter" | "project";
  id?: number;
};

export function useReportOpen() {
  return useMutation({
    mutationFn: async (query: ReportOpenInput) => {
      const response = await apiClient.openReports(query);
      return unwrapEnvelope<ApiReportOpenData>(
        response.data,
        "Could not resolve latest report path.",
      );
    },
  });
}
