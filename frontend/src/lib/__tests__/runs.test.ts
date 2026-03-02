import { describe, expect, it } from "vitest";
import { runHistoryFromApi } from "../runs";

describe("runHistoryFromApi", () => {
  it("maps chapter scope to chapterId", () => {
    const result = runHistoryFromApi({
      run_id: "r1",
      scope: "chapter:3",
      gate: "pass",
      created_at: "2024-01-01T00:00:00Z",
    });
    expect(result.id).toBe("r1");
    expect(result.scope).toBe("chapter");
    expect(result.chapterId).toBe(3);
    expect(result.gate).toBe("pass");
  });

  it("maps project scope with undefined chapterId", () => {
    const result = runHistoryFromApi({
      run_id: "r2",
      scope: "project",
      gate: "fail",
      created_at: "2024-01-02T00:00:00Z",
    });
    expect(result.scope).toBe("project");
    expect(result.chapterId).toBeUndefined();
  });
});
