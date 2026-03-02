"use client";

import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export type ChapterFilterState = {
  gate: string;
  severity: string;
  changed: string;
};

export function ChapterFilters({
  value,
  onChange,
}: {
  value: ChapterFilterState;
  onChange: (value: ChapterFilterState) => void;
}) {
  return (
    <div className="grid gap-3 rounded-md border p-3 sm:grid-cols-3">
      <div className="space-y-2">
        <Label>Gate</Label>
        <Select
          value={value.gate}
          onValueChange={(gate) => onChange({ ...value, gate })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Any gate" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="pass">Pass</SelectItem>
            <SelectItem value="fail">Fail</SelectItem>
            <SelectItem value="pass_with_waivers">Pass with waivers</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Severity</Label>
        <Select
          value={value.severity}
          onValueChange={(severity) => onChange({ ...value, severity })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Any severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Changed</Label>
        <Select
          value={value.changed}
          onValueChange={(changed) => onChange({ ...value, changed })}
        >
          <SelectTrigger>
            <SelectValue placeholder="Any" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="recent">Recently changed</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
