export type RunHistoryEntry = {
  id: string;
  scope: "chapter" | "project";
  chapterId?: number;
  gate: string;
  createdAt: string;
};

const RUN_HISTORY_KEY = "bookops.run-history";
const MAX_RUN_HISTORY = 30;

function canUseStorage() {
  return typeof window !== "undefined";
}

export function readRunHistory(): RunHistoryEntry[] {
  if (!canUseStorage()) {
    return [];
  }

  try {
    const raw = window.localStorage.getItem(RUN_HISTORY_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw) as RunHistoryEntry[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function writeRunHistory(entries: RunHistoryEntry[]) {
  if (!canUseStorage()) {
    return;
  }

  try {
    window.localStorage.setItem(
      RUN_HISTORY_KEY,
      JSON.stringify(entries.slice(0, MAX_RUN_HISTORY)),
    );
  } catch {
    // storage disabled or quota exceeded – fail silently
  }
}

export function addRunHistoryEntry(entry: RunHistoryEntry) {
  const current = readRunHistory();
  writeRunHistory([entry, ...current].slice(0, MAX_RUN_HISTORY));
}
