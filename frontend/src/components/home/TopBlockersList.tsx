import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/shared/EmptyState";
import { SeverityBadge } from "@/components/shared/SeverityBadge";

type Blocker = {
  id?: string;
  severity?: string;
  message?: string;
  scope?: string;
};

export function TopBlockersList({ blockers }: { blockers: Blocker[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Blockers</CardTitle>
      </CardHeader>
      <CardContent>
        {blockers.length === 0 ? (
          <EmptyState title="No blockers" description="Open-issues artifact has no critical/high blockers." />
        ) : (
          <ul className="space-y-2">
            {blockers.map((item) => (
              <li key={item.id} className="rounded-md border p-3">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-medium">{item.id}</p>
                  <SeverityBadge severity={item.severity ?? "info"} />
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{item.message}</p>
                <p className="mt-1 text-xs text-muted-foreground">Scope: {item.scope}</p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
