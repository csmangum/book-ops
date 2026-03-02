"use client";

import { Checkbox } from "@/components/ui/checkbox";

const filterTypes = ["character", "object", "event", "faction", "location"];

export function CanonGraphFilters({
  selectedTypes,
  onToggle,
}: {
  selectedTypes: string[];
  onToggle: (type: string, checked: boolean) => void;
}) {
  return (
    <div className="flex flex-wrap gap-4 rounded-md border p-3">
      {filterTypes.map((type) => (
        <label key={type} className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={selectedTypes.includes(type)}
            onCheckedChange={(checked) => onToggle(type, Boolean(checked))}
          />
          {type}
        </label>
      ))}
    </div>
  );
}
