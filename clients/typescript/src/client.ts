import createClient, { type Client, type ClientOptions } from "openapi-fetch";
import type { components, paths } from "./generated/schema.js";

export type BookOpsPaths = paths;
export type BookOpsComponents = components;

export type AnalyzeChapterRequest = components["schemas"]["AnalyzeChapterRequest"];
export type AnalyzeProjectRequest = components["schemas"]["AnalyzeProjectRequest"];
export type GateChapterRequest = components["schemas"]["GateChapterRequest"];
export type GateProjectRequest = components["schemas"]["GateProjectRequest"];
export type PipelineChapterRequest = components["schemas"]["PipelineChapterRequest"];
export type PipelineProjectRequest = components["schemas"]["PipelineProjectRequest"];
export type IssueUpdateRequest = components["schemas"]["IssueUpdateRequest"];
export type IssueWaiveRequest = components["schemas"]["IssueWaiveRequest"];
export type LoreDeltaRequest = components["schemas"]["LoreDeltaRequest"];
export type LoreApproveRequest = components["schemas"]["LoreApproveRequest"];
export type LoreSyncRequest = components["schemas"]["LoreSyncRequest"];
export type ReportBuildRequest = components["schemas"]["ReportBuildRequest"];
export type SettingsPatchRequest = components["schemas"]["SettingsPatchRequest"];

export type BookOpsHttpClient = Client<paths, "application/json">;

export function createBookOpsHttpClient(options: ClientOptions = {}): BookOpsHttpClient {
  return createClient<paths>({ ...options });
}

export class BookOpsApiClient {
  constructor(private readonly client: BookOpsHttpClient) {}

  static create(baseUrl = "/api", options: Omit<ClientOptions, "baseUrl"> = {}): BookOpsApiClient {
    return new BookOpsApiClient(createBookOpsHttpClient({ baseUrl, ...options }));
  }

  getVersion() {
    return this.client.GET("/version");
  }

  listAgents() {
    return this.client.GET("/agents");
  }

  runAgent(body: components["schemas"]["AgentRunRequest"]) {
    return this.client.POST("/agent/run", { body });
  }

  getChapterAgentResultsArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/agent-results", {
      params: { path: { chapterId } },
    });
  }

  rebuildIndex() {
    return this.client.POST("/index/rebuild");
  }

  getIndexStatus(includeSymbolic?: boolean) {
    return this.client.GET("/index/status", {
      params: { query: { include_symbolic: includeSymbolic } },
    });
  }

  buildCanon() {
    return this.client.POST("/canon/build");
  }

  validateCanon() {
    return this.client.GET("/canon/validate");
  }

  diffCanon(body: components["schemas"]["CanonDiffRequest"]) {
    return this.client.POST("/canon/diff", { body });
  }

  analyzeChapter(body: AnalyzeChapterRequest) {
    return this.client.POST("/analyze/chapter", { body });
  }

  analyzeProject(body: AnalyzeProjectRequest = {}) {
    return this.client.POST("/analyze/project", { body });
  }

  gateChapter(body: GateChapterRequest) {
    return this.client.POST("/gate/chapter", { body });
  }

  gateProject(body: GateProjectRequest = { strict: false }) {
    return this.client.POST("/gate/project", { body });
  }

  runChapterPipeline(body: PipelineChapterRequest) {
    return this.client.POST("/pipeline/chapter", { body });
  }

  runProjectPipeline(body: PipelineProjectRequest = { strict: false }) {
    return this.client.POST("/pipeline/project", { body });
  }

  listIssues(
    query: {
      status?: components["schemas"]["IssueStatus"];
      severity?: components["schemas"]["IssueSeverity"];
      scope?: string;
    } = {},
  ) {
    return this.client.GET("/issues", { params: { query } });
  }

  updateIssue(issueId: string, body: IssueUpdateRequest) {
    return this.client.PATCH("/issues/{issueId}", {
      params: { path: { issueId } },
      body,
    });
  }

  waiveIssue(issueId: string, body: IssueWaiveRequest) {
    return this.client.POST("/issues/{issueId}/waive", {
      params: { path: { issueId } },
      body,
    });
  }

  generateLoreDelta(body: LoreDeltaRequest) {
    return this.client.POST("/lore/delta", { body });
  }

  approveLoreProposal(body: LoreApproveRequest) {
    return this.client.POST("/lore/approve", { body });
  }

  applyLoreProposal(body: LoreSyncRequest) {
    return this.client.POST("/lore/sync", { body });
  }

  buildReports(body: ReportBuildRequest) {
    return this.client.POST("/reports/build", { body });
  }

  openReports(query: { scope: "chapter" | "project"; id?: number }) {
    return this.client.GET("/reports/open", { params: { query } });
  }

  listRuns() {
    return this.client.GET("/runs");
  }

  getRun(runId: string) {
    return this.client.GET("/runs/{runId}", {
      params: { path: { runId } },
    });
  }

  getChapterContent(chapterId: number) {
    return this.client.GET("/chapters/{chapterId}/content", {
      params: { path: { chapterId } },
    });
  }

  getCanonGraph() {
    return this.client.GET("/canon/graph");
  }

  getRules() {
    return this.client.GET("/rules");
  }

  getSettings() {
    return this.client.GET("/settings");
  }

  patchSettings(body: SettingsPatchRequest) {
    return this.client.PATCH("/settings", { body });
  }

  getChapterAnalysisArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/analysis", {
      params: { path: { chapterId } },
    });
  }

  getChapterGateArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/gate", {
      params: { path: { chapterId } },
    });
  }

  getChapterDecisionLogArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/decision-log", {
      params: { path: { chapterId } },
    });
  }

  getChapterContinuityArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/continuity", {
      params: { path: { chapterId } },
    });
  }

  getChapterStyleAuditArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/style-audit", {
      params: { path: { chapterId } },
    });
  }

  getChapterLoreDeltaArtifact(chapterId: number) {
    return this.client.GET("/artifacts/chapter/{chapterId}/lore-delta", {
      params: { path: { chapterId } },
    });
  }

  getProjectGateArtifact() {
    return this.client.GET("/artifacts/project/gate");
  }

  getProjectOpenIssuesArtifact() {
    return this.client.GET("/artifacts/project/open-issues");
  }

  getProjectResolvedIssuesArtifact() {
    return this.client.GET("/artifacts/project/resolved-issues");
  }

  getProjectTimelineArtifact() {
    return this.client.GET("/artifacts/project/timeline");
  }

  getProjectMotifsArtifact() {
    return this.client.GET("/artifacts/project/motifs");
  }
}
