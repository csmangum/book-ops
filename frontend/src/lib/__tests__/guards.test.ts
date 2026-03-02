import { describe, expect, it } from "vitest";
import { asArray, asRecord } from "../guards";

describe("guards", () => {
  describe("asRecord", () => {
    it("returns record for plain object", () => {
      const obj = { a: 1, b: "x" };
      expect(asRecord(obj)).toEqual(obj);
    });

    it("returns undefined for null", () => {
      expect(asRecord(null)).toBeUndefined();
    });

    it("returns undefined for array", () => {
      expect(asRecord([1, 2])).toBeUndefined();
    });

    it("returns undefined for primitive", () => {
      expect(asRecord("string")).toBeUndefined();
      expect(asRecord(42)).toBeUndefined();
    });
  });

  describe("asArray", () => {
    it("returns array as-is", () => {
      const arr = [1, 2, 3];
      expect(asArray(arr)).toEqual(arr);
    });

    it("returns empty array for non-array", () => {
      expect(asArray(null)).toEqual([]);
      expect(asArray(undefined)).toEqual([]);
      expect(asArray({})).toEqual([]);
    });
  });
});
