import Link from "next/link";

import type { ChapterRecord } from "@/lib/chapters";

export function ChapterNavigator({
  chapters,
  activeChapterId,
}: {
  chapters: ChapterRecord[];
  activeChapterId: number;
}) {
  return (
    <nav className="space-y-1 rounded-md border p-2">
      {chapters.map((chapter) => (
        <Link
          key={chapter.path}
          href={`/chapters/${chapter.chapterId}`}
          className={`block rounded px-2 py-1 text-sm ${
            chapter.chapterId === activeChapterId
              ? "bg-primary text-primary-foreground"
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          }`}
        >
          {chapter.chapterId}. {chapter.title}
        </Link>
      ))}
    </nav>
  );
}
