import { EmptyState } from "@/components/shared/EmptyState";

export function RulesVersionDiff() {
  return (
    <EmptyState
      title="Rule version diff unavailable"
      description="Rule versioning endpoints are not yet available in the current API."
    />
  );
}
