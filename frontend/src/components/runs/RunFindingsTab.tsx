import { EmptyState } from "@/components/shared/EmptyState";

export function RunFindingsTab() {
  return (
    <EmptyState
      title="Run findings unavailable"
      description="Backend run detail endpoint is not yet available. Use chapter/project artifact pages for findings."
    />
  );
}
