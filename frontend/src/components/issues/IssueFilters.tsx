"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { ApiIssueSeverity, ApiIssueStatus } from "@/lib/api";

export type IssueFilterState = {
  scope: string;
  severity: ApiIssueSeverity | "all";
  status: ApiIssueStatus | "all";
  query: string;
};

export function IssueFilters({
  value,
  onChange,
}: {
  value: IssueFilterState;
  onChange: (next: IssueFilterState) => void;
}) {
  return (
    <div className="grid gap-3 rounded-md border p-3 md:grid-cols-4">
      <div className="space-y-2">
        <Label>Scope</Label>
        <Select value={value.scope} onValueChange={(scope) => onChange({ ...value, scope })}>
          <SelectTrigger>
            <SelectValue placeholder="Any scope" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="project">Project</SelectItem>
            <SelectItem value="chapter">Chapter</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Severity</Label>
        <Select
          value={value.severity}
          onValueChange={(severity) =>
            onChange({
              ...value,
              severity: severity as ApiIssueSeverity | "all",
            })
          }
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
            <SelectItem value="info">Info</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Status</Label>
        <Select
          value={value.status}
          onValueChange={(status) =>
            onChange({
              ...value,
              status: status as ApiIssueStatus | "all",
            })
          }
        >
          <SelectTrigger>
            <SelectValue placeholder="Any status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="in_progress">In progress</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="waived">Waived</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-2">
        <Label>Search</Label>
        <Input
          value={value.query}
          onChange={(event) => onChange({ ...value, query: event.target.value })}
          placeholder="rule ID, message..."
        />
      </div>
    </div>
  );
}
