"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import {
  apiClient,
  type ApiSettingsData,
  type ApiSettingsPatchRequest,
} from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export function useSettings() {
  return useQuery({
    queryKey: queryKeys.settings,
    queryFn: async () => {
      const response = await apiClient.getSettings();
      return unwrapEnvelope<ApiSettingsData>(
        response.data,
        "Could not load settings.",
      );
    },
  });
}

export function usePatchSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (patch: ApiSettingsPatchRequest) => {
      const response = await apiClient.patchSettings(patch);
      return unwrapEnvelope<ApiSettingsData>(
        response.data,
        "Could not update settings.",
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.settings });
    },
  });
}
