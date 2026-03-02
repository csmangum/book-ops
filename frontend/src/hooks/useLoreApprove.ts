"use client";

import { useMutation } from "@tanstack/react-query";

import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type LoreApproveRequest = ApiComponents["schemas"]["LoreApproveRequest"];

export function useLoreApprove() {
  return useMutation({
    mutationFn: async (body: LoreApproveRequest) => {
      const response = await apiClient.approveLoreProposal(body);
      return unwrapEnvelope(response.data, "Could not approve lore proposal.");
    },
  });
}
