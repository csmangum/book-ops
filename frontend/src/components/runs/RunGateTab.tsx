import { EmptyState } from "@/components/shared/EmptyState";

export function RunGateTab() {
  return (
    <EmptyState
      title="Run gate detail unavailable"
      description="Run-scoped gate artifact retrieval is pending backend API support."
    />
  );
}
