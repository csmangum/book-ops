import { describe, expect, it } from "vitest";

import { ApiEnvelopeError, unwrapEnvelope } from "@/lib/api-envelope";

describe("unwrapEnvelope", () => {
  it("returns data for ok responses", () => {
    const result = unwrapEnvelope({
      ok: true,
      exit_code: 0,
      data: { value: 42 },
      stderr: "",
    });

    expect(result).toEqual({ value: 42 });
  });

  it("throws ApiEnvelopeError for failed responses", () => {
    expect(() =>
      unwrapEnvelope({
        ok: false,
        exit_code: 2,
        data: {},
        stderr: "gate failed",
      }),
    ).toThrow(ApiEnvelopeError);
  });
});
