import { EmptyState } from "@/components/shared/EmptyState";

export function DecisionLogViewer() {
  return (
    <EmptyState
      title="Decision log unavailable"
      description="Run-scoped decision log endpoint is not yet exposed by the backend."
    />
  );
}
