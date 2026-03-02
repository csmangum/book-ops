import { EmptyState } from "@/components/shared/EmptyState";

type Marker = {
  chapter: number;
  day_markers?: string[];
  date_markers?: string[];
};

export function TimelineConflictList({ markers }: { markers: Marker[] }) {
  const conflicts = markers.filter((marker) => (marker.day_markers ?? []).length > 1);

  if (conflicts.length === 0) {
    return (
      <EmptyState
        title="No timeline conflicts flagged"
        description="Conflict overlays are based on timeline artifact markers."
      />
    );
  }

  return (
    <ul className="space-y-2">
      {conflicts.map((marker) => (
        <li key={marker.chapter} className="rounded-md border p-2 text-sm">
          <p className="font-medium">Chapter {marker.chapter}</p>
          <p className="text-muted-foreground">
            Day markers: {(marker.day_markers ?? []).join(", ")}
          </p>
        </li>
      ))}
    </ul>
  );
}
