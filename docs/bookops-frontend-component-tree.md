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
