import { EmptyState } from "@/components/shared/EmptyState";

type Provenance = {
  file: string;
  line?: number;
};

export function ProvenanceList({ provenance }: { provenance: Provenance[] }) {
  if (provenance.length === 0) {
    return (
      <EmptyState
        title="No provenance available"
        description="Canonical provenance references require graph artifact endpoint support."
      />
    );
  }

  return (
    <ul className="space-y-2 text-sm">
      {provenance.map((item) => (
        <li key={`${item.file}-${item.line ?? 0}`} className="rounded-md border p-2">
          {item.file}
          {item.line ? `:${item.line}` : ""}
        </li>
      ))}
    </ul>
  );
}
