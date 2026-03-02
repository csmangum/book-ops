"use client";

import { useMutation } from "@tanstack/react-query";

import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type GateChapterRequest = ApiComponents["schemas"]["GateChapterRequest"];

export function useGateChapter() {
  return useMutation({
    mutationFn: async (body: GateChapterRequest) => {
      const response = await apiClient.gateChapter(body);
      return unwrapEnvelope(response.data, "Could not run chapter gate.");
    },
  });
}
