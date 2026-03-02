"use client";

import { useMutation } from "@tanstack/react-query";

import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type GateProjectRequest = ApiComponents["schemas"]["GateProjectRequest"];

export function useGateProject() {
  return useMutation({
    mutationFn: async (body?: GateProjectRequest) => {
      const response = await apiClient.gateProject(body ?? { strict: false });
      return unwrapEnvelope(response.data, "Could not run project gate.");
    },
  });
}
