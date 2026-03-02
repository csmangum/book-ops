export type AppError = {
  message: string;
  details?: string;
};

export function toAppError(error: unknown, fallback = "Something went wrong.") {
  if (error instanceof Error) {
    return {
      message: error.message || fallback,
      details: error.stack,
    } satisfies AppError;
  }

  if (typeof error === "string") {
    return { message: error } satisfies AppError;
  }

  return { message: fallback } satisfies AppError;
}
