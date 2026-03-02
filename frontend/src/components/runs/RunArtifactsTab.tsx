import { EmptyState } from "@/components/shared/EmptyState";

export function RunArtifactsTab() {
  return (
    <EmptyState
      title="Run artifacts unavailable"
      description="Use chapter/project artifact endpoints until run-specific artifact APIs are added."
    />
  );
}
