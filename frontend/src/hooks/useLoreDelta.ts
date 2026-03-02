"use client";

import { useMutation } from "@tanstack/react-query";

import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type LoreDeltaRequest = ApiComponents["schemas"]["LoreDeltaRequest"];

export function useLoreDelta() {
  return useMutation({
    mutationFn: async (body: LoreDeltaRequest) => {
      const response = await apiClient.generateLoreDelta(body);
      return unwrapEnvelope(response.data, "Could not generate lore delta.");
    },
  });
}
