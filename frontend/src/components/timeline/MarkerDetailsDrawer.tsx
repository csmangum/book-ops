"use client";

import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";

type Marker = {
  chapter: number;
  day_markers?: string[];
  date_markers?: string[];
};

export function MarkerDetailsDrawer({
  marker,
  open,
  onOpenChange,
}: {
  marker?: Marker;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <div className="mx-auto w-full max-w-2xl p-4">
          {marker ? (
            <>
              <DrawerHeader className="px-0">
                <DrawerTitle>Chapter {marker.chapter} marker</DrawerTitle>
                <DrawerDescription>Timeline marker details and source references.</DrawerDescription>
              </DrawerHeader>
              <div className="space-y-2 rounded-md border p-3 text-sm">
                <p>
                  <span className="font-medium">Day markers:</span>{" "}
                  {(marker.day_markers ?? []).join(", ") || "none"}
                </p>
                <p>
                  <span className="font-medium">Date markers:</span>{" "}
                  {(marker.date_markers ?? []).join(", ") || "none"}
                </p>
              </div>
            </>
          ) : null}
        </div>
      </DrawerContent>
    </Drawer>
  );
}
