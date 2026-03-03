# BookOps Frontend Component Tree (React by Route)

This tree is structured for a Next.js App Router frontend.

```text
src/
  app/
    layout.tsx
    providers.tsx
    (routes)/
      page.tsx                          # /
      chapters/
        page.tsx                        # /chapters
        [chapterId]/
          page.tsx                      # /chapters/:chapterId
      lore/
        page.tsx                        # /lore
        [proposalId]/
          page.tsx                      # /lore/:proposalId
      timeline/
        page.tsx                        # /timeline
      canon/
        page.tsx                        # /canon
      rules/
        page.tsx                        # /rules
      runs/
        page.tsx                        # /runs
        [runId]/
          page.tsx                      # /runs/:runId
      issues/
        page.tsx                        # /issues
      settings/
        page.tsx                        # /settings

  components/
    shell/
      AppShell.tsx
      SidebarNav.tsx
      TopBar.tsx
      GlobalSearch.tsx
      ProjectBranchBadge.tsx
      RunPipelineButton.tsx

    home/
      GateStatusCards.tsx
      TopBlockersList.tsx
      RecentRunsList.tsx
      ChangedSinceLastRun.tsx
      QuickActions.tsx

    chapters/
      ChapterTable.tsx
      ChapterFilters.tsx
      ChapterNavigator.tsx
      ManuscriptEditor.tsx
      ManuscriptDiffToggle.tsx
      FindingsPanel.tsx
      FindingCard.tsx
      EvidenceSnippet.tsx
      TriageActions.tsx

    lore/
      ProposalQueue.tsx
      ProposalStatusTabs.tsx
      LoreDiffViewer.tsx
      ProposalEvidencePanel.tsx
      ApproveRejectActions.tsx
      ApplyProposalButton.tsx

    timeline/
      TimelineRail.tsx
      TimelineFilters.tsx
      TimelineConflictList.tsx
      MarkerDetailsDrawer.tsx

    canon/
      CanonGraphCanvas.tsx
      CanonGraphFilters.tsx
      EntityInspector.tsx
      ProvenanceList.tsx

    rules/
      RuleList.tsx
      RuleDetailDrawer.tsx
      ThresholdEditor.tsx
      RuleSandboxRunner.tsx
      RulesVersionDiff.tsx

    runs/
      RunsTable.tsx
      RunSummary.tsx
      RunFindingsTab.tsx
      RunGateTab.tsx
      RunArtifactsTab.tsx
      DecisionLogViewer.tsx

    issues/
      IssuesKanban.tsx
      IssuesTable.tsx
      IssueFilters.tsx
      IssueDrawer.tsx
      BulkIssueActions.tsx

    shared/
      SeverityBadge.tsx
      GateBadge.tsx
      StatusBadge.tsx
      JsonViewer.tsx
      MarkdownViewer.tsx
      EmptyState.tsx
      LoadingState.tsx
      ErrorBanner.tsx

  hooks/
    useVersion.ts
    useIndexStatus.ts
    useAnalyzeChapter.ts
    useAnalyzeProject.ts
    useIssueList.ts
    useIssueUpdate.ts
    useLoreDelta.ts
    useLoreApprove.ts
    useLoreSync.ts
    useGateChapter.ts
    useGateProject.ts
    usePipelineRun.ts
    useReportOpen.ts
```

## Hook to API mapping

Each hook typically wraps one or more API calls. Use this to trace data flow and avoid duplicate requests:

| Hook | Endpoint(s) |
|------|-------------|
| `useVersion` | `GET /api/version` |
| `useIndexStatus` | `GET /api/index/status` (query: `include_symbolic`) |
| `useAnalyzeChapter` | `POST /api/analyze/chapter` (body: chapter_id, optional checks, since) |
| `useAnalyzeProject` | `POST /api/analyze/project` (body: optional since) |
| `useIssueList` | `GET /api/issues` (query: scope, status, severity) |
| `useIssueUpdate` | `PATCH /api/issues/:issueId` (body: status, note) |
| `useLoreDelta` | `POST /api/lore/delta` (body: scope, id, since) |
| `useLoreApprove` | `POST /api/lore/approve` (body: proposal, reviewer, note) |
| `useLoreSync` | `POST /api/lore/sync` (body: proposal, apply) |
| `useGateChapter` | `POST /api/gate/chapter` (body: chapter_id, strict) |
| `useGateProject` | `POST /api/gate/project` (body: optional strict) |
| `usePipelineRun` | `POST /api/pipeline/chapter` or `POST /api/pipeline/project` (body: chapter_id for chapter, optional strict) |
| `useReportOpen` | `GET /api/reports/open` (query: scope, id) |

Additional reads (e.g. run list, run detail, chapter content, rules, settings, artifacts) are typically done via direct client calls or dedicated hooks; see [bookops-backend-api-contract.md](bookops-backend-api-contract.md) for the full endpoint list.

## Shared types

Request and response types should come from the **generated API client** so components and hooks share a single source of truth:

- **Schema and types:** `clients/typescript/src/generated/schema.ts` (or equivalent generated from `openapi/bookops-api.openapi.yaml`).
- **Client:** `clients/typescript/src/client.ts` — use the typed client methods in hooks and data-fetching layers rather than ad-hoc `fetch` and hand-written types.

Use these types for props (e.g. `Issue`, `GateResult`, `Run`, envelope `data` shapes) and for hook return values so the UI stays in sync with the API contract.

## Route-to-component mapping

- `/`: `GateStatusCards`, `TopBlockersList`, `RecentRunsList`, `QuickActions`
- `/chapters`: `ChapterTable`, `ChapterFilters`
- `/chapters/:id`: `ChapterNavigator`, `ManuscriptEditor`, `FindingsPanel`
- `/lore`: `ProposalQueue`, `ProposalStatusTabs`
- `/lore/:proposalId`: `LoreDiffViewer`, `ProposalEvidencePanel`, `ApproveRejectActions`
- `/timeline`: `TimelineRail`, `TimelineConflictList`
- `/canon`: `CanonGraphCanvas`, `EntityInspector`
- `/rules`: `RuleList`, `RuleDetailDrawer`, `ThresholdEditor`
- `/runs`: `RunsTable`
- `/runs/:runId`: `RunSummary`, `RunGateTab`, `DecisionLogViewer`
- `/issues`: `IssuesKanban`, `IssuesTable`
- `/settings`: configuration forms and identity defaults
