import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/shared/EmptyState";
import type { ChapterRecord } from "@/lib/chapters";

export function ChangedSinceLastRun({ chapters }: { chapters: ChapterRecord[] }) {
  const sorted = [...chapters]
    .sort((a, b) => b.modifiedAt - a.modifiedAt)
    .slice(0, 8);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Changed Since Last Run</CardTitle>
      </CardHeader>
      <CardContent>
        {sorted.length === 0 ? (
          <EmptyState title="No chapters indexed" description="Run index rebuild to populate chapter metadata." />
        ) : (
          <ul className="space-y-2 text-sm">
            {sorted.map((chapter) => (
              <li key={chapter.path} className="rounded-md border p-2">
                <p className="font-medium">
                  Chapter {chapter.chapterId}: {chapter.title}
                </p>
                <p className="text-xs text-muted-foreground">
                  Last modified {new Date(chapter.modifiedAt * 1000).toLocaleString()}
                </p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
