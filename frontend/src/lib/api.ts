type ApiEnvelope<T = Record<string, unknown>> = {
  ok: boolean;
  exit_code: number;
  data: T;
  stderr: string;
};

export type ApiVersionData = {
  bookops_version: string;
  rules_schema_version: number;
  canon_schema_version: number;
  agent_pack_version: string;
  agent_count: number;
};

export type ApiIndexStatusData = {
  symbolic_exists: boolean;
  semantic_exists: boolean;
  symbolic_path: string;
  semantic_path: string;
  index_version?: number | null;
  generated_at?: string | null;
  file_count?: number | null;
  corpus_hash?: string | null;
  semantic_status?: string | null;
  semantic_source_file_count?: number | null;
};

export type ApiIndexRebuildData = {
  index_version: number;
  generated_at: string;
  project_root: string;
  file_count: number;
  excluded_dirs: string[];
  corpus_hash: string;
  symbolic: ApiComponents["schemas"]["IndexEntry"][];
};

export type ApiGateData = {
  status: ApiComponents["schemas"]["GateStatus"];
  blocking_issue_ids: string[];
  warning_issue_ids: string[];
  message: string;
};

export type ApiPipelineData = {
  gate: ApiComponents["schemas"]["GateStatus"];
  scope: string;
};

export type ApiIssueListData = {
  count: number;
  issues: ApiComponents["schemas"]["Issue"][];
};

export type ApiIssueMutateData = {
  updated?: string | null;
  waived?: string | null;
  issue_count: number;
};

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

export type ApiLoreDeltaData = {
  scope: string;
  chapter_count_evaluated: number;
  proposals: ApiLoreProposal[];
};

export type ApiLoreApproveData = {
  approved: string;
  reviewer: string;
};

export type ApiLoreSyncData = {
  applied: string;
  target: string;
};

export type ApiReportOpenData = {
  path: string;
};

export type ApiComponents = {
  schemas: {
    IndexEntry: {
      path: string;
      sha256: string;
      size: number;
      line_count: number;
      modified_at: number;
    };
    AnalyzeChapterRequest: {
      chapter_id: number;
      checks?: string[];
      since?: string | null;
    };
    AnalyzeProjectRequest: {
      since?: string | null;
    };
    GateChapterRequest: {
      chapter_id: number;
      strict?: boolean;
    };
    GateProjectRequest: {
      strict?: boolean;
    };
    PipelineChapterRequest: {
      chapter_id: number;
      strict?: boolean;
    };
    PipelineProjectRequest: {
      strict?: boolean;
    };
    IssueStatus: "open" | "in_progress" | "resolved" | "waived";
    IssueSeverity: "critical" | "high" | "medium" | "low" | "info";
    IssueUpdateRequest: {
      status: "open" | "in_progress" | "resolved" | "waived";
      note?: string;
    };
    IssueWaiveRequest: {
      reason: string;
      reviewer: string;
    };
    LoreDeltaRequest: {
      scope: "chapter" | "project";
      id?: number | null;
      since?: string | null;
    };
    LoreApproveRequest: {
      proposal: string;
      reviewer: string;
      note?: string;
    };
    LoreSyncRequest: {
      proposal: string;
      apply: boolean;
    };
    Issue: {
      id: string;
      rule_id: string;
      severity: "critical" | "high" | "medium" | "low" | "info";
      status: "open" | "in_progress" | "resolved" | "waived";
      scope: string;
      message: string;
      evidence?: Array<{
        file?: string;
        line_start?: number;
        line_end?: number;
        excerpt?: string;
      }>;
    };
    GateStatus: "pass" | "fail" | "pass_with_waivers";
  };
};

export type ApiIssue = ApiComponents["schemas"]["Issue"];
export type ApiIssueStatus = ApiComponents["schemas"]["IssueStatus"];
export type ApiIssueSeverity = ApiComponents["schemas"]["IssueSeverity"];
export type ApiGateStatus = ApiComponents["schemas"]["GateStatus"];

function withQuery(path: string, query: Record<string, unknown>) {
  const search = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    search.set(key, String(value));
  });

  return search.size ? `${path}?${search.toString()}` : path;
}

export class BookOpsApiClient {
  constructor(private readonly baseUrl: string) {}

  static create(baseUrl = "/api") {
    return new BookOpsApiClient(baseUrl);
  }

  private async request<TData>(
    path: string,
    init?: RequestInit,
  ): Promise<{ data: ApiEnvelope<TData> }> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });

    const data = (await response.json()) as ApiEnvelope<TData>;
    return { data };
  }

  getVersion() {
    return this.request<ApiVersionData>("/version");
  }

  rebuildIndex() {
    return this.request<ApiIndexRebuildData>("/index/rebuild", { method: "POST" });
  }

  getIndexStatus() {
    return this.request<ApiIndexStatusData>("/index/status");
  }

  buildCanon() {
    return this.request("/canon/build", { method: "POST" });
  }

  validateCanon() {
    return this.request("/canon/validate");
  }

  diffCanon(body: { from_snapshot: string; to_snapshot: string }) {
    return this.request("/canon/diff", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  analyzeChapter(body: ApiComponents["schemas"]["AnalyzeChapterRequest"]) {
    return this.request("/analyze/chapter", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  analyzeProject(body: ApiComponents["schemas"]["AnalyzeProjectRequest"] = {}) {
    return this.request("/analyze/project", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  gateChapter(body: ApiComponents["schemas"]["GateChapterRequest"]) {
    return this.request<ApiGateData>("/gate/chapter", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  gateProject(body: ApiComponents["schemas"]["GateProjectRequest"] = { strict: false }) {
    return this.request<ApiGateData>("/gate/project", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  runChapterPipeline(body: ApiComponents["schemas"]["PipelineChapterRequest"]) {
    return this.request<ApiPipelineData>("/pipeline/chapter", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  runProjectPipeline(body: ApiComponents["schemas"]["PipelineProjectRequest"] = { strict: false }) {
    return this.request<ApiPipelineData>("/pipeline/project", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  listIssues(
    query: {
      status?: ApiIssueStatus;
      severity?: ApiIssueSeverity;
      scope?: string;
    } = {},
  ) {
    return this.request<ApiIssueListData>(withQuery("/issues", query));
  }

  updateIssue(issueId: string, body: ApiComponents["schemas"]["IssueUpdateRequest"]) {
    return this.request<ApiIssueMutateData>(`/issues/${issueId}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    });
  }

  waiveIssue(issueId: string, body: ApiComponents["schemas"]["IssueWaiveRequest"]) {
    return this.request<ApiIssueMutateData>(`/issues/${issueId}/waive`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  generateLoreDelta(body: ApiComponents["schemas"]["LoreDeltaRequest"]) {
    return this.request<ApiLoreDeltaData>("/lore/delta", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  approveLoreProposal(body: ApiComponents["schemas"]["LoreApproveRequest"]) {
    return this.request<ApiLoreApproveData>("/lore/approve", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  applyLoreProposal(body: ApiComponents["schemas"]["LoreSyncRequest"]) {
    return this.request<ApiLoreSyncData>("/lore/sync", {
      method: "POST",
      body: JSON.stringify(body),
    });
  }

  openReports(query: { scope: "chapter" | "project"; id?: number }) {
    return this.request<ApiReportOpenData>(withQuery("/reports/open", query));
  }

  getChapterAnalysisArtifact(chapterId: number) {
    return this.request(`/artifacts/chapter/${chapterId}/analysis`);
  }

  getChapterGateArtifact(chapterId: number) {
    return this.request(`/artifacts/chapter/${chapterId}/gate`);
  }

  getChapterDecisionLogArtifact(chapterId: number) {
    return this.request(`/artifacts/chapter/${chapterId}/decision-log`);
  }

  getChapterContinuityArtifact(chapterId: number) {
    return this.request(`/artifacts/chapter/${chapterId}/continuity`);
  }

  getChapterStyleAuditArtifact(chapterId: number) {
    return this.request(`/artifacts/chapter/${chapterId}/style-audit`);
  }

  getChapterLoreDeltaArtifact(chapterId: number) {
    return this.request(`/artifacts/chapter/${chapterId}/lore-delta`);
  }

  getProjectGateArtifact() {
    return this.request("/artifacts/project/gate");
  }

  getProjectOpenIssuesArtifact() {
    return this.request("/artifacts/project/open-issues");
  }

  getProjectResolvedIssuesArtifact() {
    return this.request("/artifacts/project/resolved-issues");
  }

  getProjectTimelineArtifact() {
    return this.request("/artifacts/project/timeline");
  }

  getProjectMotifsArtifact() {
    return this.request("/artifacts/project/motifs");
  }
}

export function resolveApiBaseUrl() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL?.trim();

  if (!apiUrl) {
    return "/api";
  }

  return apiUrl.endsWith("/") ? apiUrl.slice(0, -1) : apiUrl;
}

export const apiClient = BookOpsApiClient.create(resolveApiBaseUrl());
