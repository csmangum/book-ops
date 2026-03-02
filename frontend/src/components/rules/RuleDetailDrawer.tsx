"use client";

import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";

type RuleItem = {
  id: string;
  kind: "hard" | "soft";
  severity: string;
  message: string;
};

export function RuleDetailDrawer({
  rule,
  open,
  onOpenChange,
}: {
  rule?: RuleItem;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <div className="mx-auto w-full max-w-2xl p-4">
          {rule ? (
            <>
              <DrawerHeader className="px-0">
                <DrawerTitle>{rule.id}</DrawerTitle>
                <DrawerDescription>
                  {rule.kind.toUpperCase()} · {rule.severity}
                </DrawerDescription>
              </DrawerHeader>
              <p className="text-sm text-muted-foreground">{rule.message}</p>
            </>
          ) : null}
        </div>
      </DrawerContent>
    </Drawer>
  );
}
