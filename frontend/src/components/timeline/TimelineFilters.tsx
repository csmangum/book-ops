"use client";

import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";

export type TimelineFilterState = {
  chapterMarkers: boolean;
  entityEvents: boolean;
  contradictions: boolean;
};

export function TimelineFilters({
  value,
  onChange,
}: {
  value: TimelineFilterState;
  onChange: (value: TimelineFilterState) => void;
}) {
  return (
    <div className="flex flex-wrap gap-6 rounded-md border p-3">
      <div className="flex items-center gap-2 text-sm">
        <Checkbox
          id="filter-chapter-markers"
          checked={value.chapterMarkers}
          onCheckedChange={(checked) =>
            onChange({ ...value, chapterMarkers: Boolean(checked) })
          }
        />
        <Label htmlFor="filter-chapter-markers">Chapter markers</Label>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <Checkbox
          id="filter-entity-events"
          checked={value.entityEvents}
          onCheckedChange={(checked) =>
            onChange({ ...value, entityEvents: Boolean(checked) })
          }
        />
        <Label htmlFor="filter-entity-events">Entity events</Label>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <Checkbox
          id="filter-contradictions"
          checked={value.contradictions}
          onCheckedChange={(checked) =>
            onChange({ ...value, contradictions: Boolean(checked) })
          }
        />
        <Label htmlFor="filter-contradictions">Contradictions</Label>
      </div>
    </div>
  );
}
