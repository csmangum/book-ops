"use client";

import { AlertTriangle, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { toAppError } from "@/lib/errors";

export function ErrorBanner({
  error,
  title = "Request failed",
}: {
  error: unknown;
  title?: string;
}) {
  const [dismissed, setDismissed] = useState(false);
  const normalized = toAppError(error, "Unknown error.");

  if (dismissed) {
    return null;
  }

  return (
    <div className="flex items-start justify-between gap-4 rounded-md border border-red-200 bg-red-50 p-3 text-red-800">
      <div className="flex gap-2">
        <AlertTriangle className="mt-0.5 size-4 shrink-0" />
        <div>
          <p className="text-sm font-semibold">{title}</p>
          <p className="text-sm">{normalized.message}</p>
        </div>
      </div>
      <Button
        variant="ghost"
        size="icon-sm"
        className="text-red-700 hover:text-red-900"
        onClick={() => setDismissed(true)}
      >
        <X className="size-4" />
      </Button>
    </div>
  );
}
