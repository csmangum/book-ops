import type { ApiComponents } from "@/lib/api";

export type SymbolicEntry = ApiComponents["schemas"]["IndexEntry"];

export type ChapterRecord = {
  chapterId: number;
  title: string;
  path: string;
  modifiedAt: number;
  size: number;
  lineCount: number;
};

const CHAPTER_FILE_RE =
  /^chapters\/(?<chapter>\d+)[_-](?<title>.+?)\.md$/i;

function titleFromSlug(slug: string) {
  return slug.replace(/[_-]+/g, " ").trim();
}

export function chapterRecordFromSymbolicEntry(
  entry: SymbolicEntry,
): ChapterRecord | null {
  const match = entry.path.match(CHAPTER_FILE_RE);
  if (!match?.groups) {
    return null;
  }

  const chapterId = Number(match.groups.chapter);
  if (!Number.isFinite(chapterId)) {
    return null;
  }

  return {
    chapterId,
    title: titleFromSlug(match.groups.title),
    path: entry.path,
    modifiedAt: entry.modified_at,
    size: entry.size,
    lineCount: entry.line_count,
  };
}

export function toChapterRecords(symbolicEntries: SymbolicEntry[]) {
  return symbolicEntries
    .map(chapterRecordFromSymbolicEntry)
    .filter((entry): entry is ChapterRecord => Boolean(entry))
    .sort((a, b) => a.chapterId - b.chapterId);
}
