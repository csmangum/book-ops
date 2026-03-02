import {
  BookOpsApiClient as GeneratedApiClient,
  type BookOpsComponents,
} from "@bookops/api-client";

export type ApiComponents = BookOpsComponents;
export type ApiVersionData = ApiComponents["schemas"]["VersionData"];
export type ApiIndexStatusData = ApiComponents["schemas"]["IndexStatusData"];
export type ApiIndexRebuildData = ApiComponents["schemas"]["IndexRebuildData"];
export type ApiGateData = ApiComponents["schemas"]["GateData"];
export type ApiPipelineData = ApiComponents["schemas"]["PipelineData"];
export type ApiIssueListData = ApiComponents["schemas"]["IssueListData"];
export type ApiIssueMutateData = ApiComponents["schemas"]["IssueMutateData"];
export type ApiLoreDeltaData = ApiComponents["schemas"]["LoreDeltaData"];
export type ApiLoreApproveData = ApiComponents["schemas"]["LoreApproveData"];
export type ApiLoreSyncData = ApiComponents["schemas"]["LoreSyncData"];
export type ApiReportOpenData = ApiComponents["schemas"]["ReportOpenData"];
export type ApiIssue = ApiComponents["schemas"]["Issue"];
export type ApiIssueStatus = ApiComponents["schemas"]["IssueStatus"];
export type ApiIssueSeverity = ApiComponents["schemas"]["IssueSeverity"];
export type ApiGateStatus = ApiComponents["schemas"]["GateStatus"];
export type ApiLoreProposal = {
  id: string;
  status?: string;
  chapter?: number;
  target_lore_file?: string;
  reason?: string;
  evidence?: Array<{
    file?: string;
    line_hint?: number;
    excerpt?: string;
  }>;
};
export const BookOpsApiClient = GeneratedApiClient;

export function resolveApiBaseUrl() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

  if (!apiUrl) {
    return "/api";
  }

  return apiUrl.endsWith("/") ? apiUrl.slice(0, -1) : apiUrl;
}

export const apiClient = GeneratedApiClient.create(resolveApiBaseUrl());
