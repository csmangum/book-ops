type Envelope<Data> = {
  ok: boolean;
  exit_code: number;
  data?: Data;
  stderr: string;
};

export class ApiEnvelopeError extends Error {
  constructor(
    message: string,
    public readonly exitCode?: number,
    public readonly stderr?: string,
  ) {
    super(message);
    this.name = "ApiEnvelopeError";
  }
}

export function unwrapEnvelope<Data>(
  payload: Envelope<Data> | undefined,
  fallbackMessage = "Unexpected API response.",
) {
  if (!payload) {
    throw new ApiEnvelopeError(fallbackMessage);
  }

  if (!payload.ok) {
    throw new ApiEnvelopeError(
      payload.stderr || fallbackMessage,
      payload.exit_code,
      payload.stderr,
    );
  }

  if (payload.data === undefined) {
    throw new ApiEnvelopeError(fallbackMessage, payload.exit_code, payload.stderr);
  }

  return payload.data;
}
