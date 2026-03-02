"use client";

import { useMutation } from "@tanstack/react-query";

import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type LoreSyncRequest = ApiComponents["schemas"]["LoreSyncRequest"];

export function useLoreSync() {
  return useMutation({
    mutationFn: async (body: LoreSyncRequest) => {
      const response = await apiClient.applyLoreProposal(body);
      return unwrapEnvelope(response.data, "Could not apply lore proposal.");
    },
  });
}
