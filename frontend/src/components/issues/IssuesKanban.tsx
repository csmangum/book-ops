import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SeverityBadge } from "@/components/shared/SeverityBadge";

type Issue = {
  id: string;
  status: string;
  severity: string;
  message: string;
};

const columns = ["open", "in_progress", "resolved", "waived"];

export function IssuesKanban({
  issues,
  onOpenIssue,
}: {
  issues: Issue[];
  onOpenIssue: (issueId: string) => void;
}) {
  return (
    <div className="grid gap-4 lg:grid-cols-4">
      {columns.map((column) => (
        <Card key={column}>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm capitalize">{column.replace("_", " ")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {issues
              .filter((issue) => issue.status === column)
              .map((issue) => (
                <button
                  type="button"
                  key={issue.id}
                  onClick={() => onOpenIssue(issue.id)}
                  className="w-full rounded-md border p-2 text-left"
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-xs font-semibold">{issue.id}</p>
                    <SeverityBadge severity={issue.severity} />
                  </div>
                  <p className="mt-1 text-xs text-muted-foreground">{issue.message}</p>
                </button>
              ))}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
