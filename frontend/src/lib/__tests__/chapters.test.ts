import { describe, expect, it } from "vitest";
import {
  chapterRecordFromSymbolicEntry,
  toChapterRecords,
} from "../chapters";

describe("chapters", () => {
  describe("chapterRecordFromSymbolicEntry", () => {
    it("parses valid chapter path", () => {
      const entry = {
        path: "chapters/1_Opening.md",
        sha256: "abc",
        size: 100,
        line_count: 10,
        modified_at: 12345,
      };
      const result = chapterRecordFromSymbolicEntry(entry);
      expect(result).not.toBeNull();
      expect(result!.chapterId).toBe(1);
      expect(result!.title).toBe("Opening");
      expect(result!.path).toBe("chapters/1_Opening.md");
    });

    it("returns null for non-chapter path", () => {
      const entry = {
        path: "other/file.md",
        sha256: "x",
        size: 0,
        line_count: 0,
        modified_at: 0,
      };
      expect(chapterRecordFromSymbolicEntry(entry)).toBeNull();
    });
  });

  describe("toChapterRecords", () => {
    it("sorts by chapterId", () => {
      const entries = [
        {
          path: "chapters/3_Three.md",
          sha256: "x",
          size: 0,
          line_count: 0,
          modified_at: 0,
        },
        {
          path: "chapters/1_One.md",
          sha256: "x",
          size: 0,
          line_count: 0,
          modified_at: 0,
        },
      ];
      const result = toChapterRecords(entries);
      expect(result[0].chapterId).toBe(1);
      expect(result[1].chapterId).toBe(3);
    });
  });
});
