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
      <label className="flex items-center gap-2 text-sm">
        <Checkbox
          checked={value.chapterMarkers}
          onCheckedChange={(checked) =>
            onChange({ ...value, chapterMarkers: Boolean(checked) })
          }
        />
        <Label>Chapter markers</Label>
      </label>
      <label className="flex items-center gap-2 text-sm">
        <Checkbox
          checked={value.entityEvents}
          onCheckedChange={(checked) =>
            onChange({ ...value, entityEvents: Boolean(checked) })
          }
        />
        <Label>Entity events</Label>
      </label>
      <label className="flex items-center gap-2 text-sm">
        <Checkbox
          checked={value.contradictions}
          onCheckedChange={(checked) =>
            onChange({ ...value, contradictions: Boolean(checked) })
          }
        />
        <Label>Contradictions</Label>
      </label>
    </div>
  );
}
