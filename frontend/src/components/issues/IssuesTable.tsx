"use client";

import { Checkbox } from "@/components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SeverityBadge, StatusBadge } from "@/components/shared";

type Issue = {
  id: string;
  rule_id: string;
  severity: string;
  status: string;
  scope: string;
  message: string;
};

export function IssuesTable({
  issues,
  selectedIssueIds,
  onSelectIssue,
  onOpenIssue,
}: {
  issues: Issue[];
  selectedIssueIds: string[];
  onSelectIssue: (issueId: string, checked: boolean) => void;
  onOpenIssue: (issueId: string) => void;
}) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-10" />
            <TableHead>ID</TableHead>
            <TableHead>Rule</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Scope</TableHead>
            <TableHead>Message</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {issues.map((issue) => (
            <TableRow key={issue.id} className="cursor-pointer" onClick={() => onOpenIssue(issue.id)}>
              <TableCell onClick={(event) => event.stopPropagation()}>
                <Checkbox
                  checked={selectedIssueIds.includes(issue.id)}
                  onCheckedChange={(checked) =>
                    onSelectIssue(issue.id, Boolean(checked))
                  }
                />
              </TableCell>
              <TableCell className="font-medium">{issue.id}</TableCell>
              <TableCell>{issue.rule_id}</TableCell>
              <TableCell>
                <SeverityBadge severity={issue.severity} />
              </TableCell>
              <TableCell>
                <StatusBadge status={issue.status} />
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">{issue.scope}</TableCell>
              <TableCell className="text-sm text-muted-foreground">{issue.message}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
