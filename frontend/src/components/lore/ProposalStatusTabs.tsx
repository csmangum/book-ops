"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

export function ProposalStatusTabs({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <Tabs value={value} onValueChange={onChange}>
      <TabsList className="grid w-full grid-cols-5">
        <TabsTrigger value="all">All</TabsTrigger>
        <TabsTrigger value="pending_review">Pending</TabsTrigger>
        <TabsTrigger value="approved">Approved</TabsTrigger>
        <TabsTrigger value="applied">Applied</TabsTrigger>
        <TabsTrigger value="rejected">Rejected</TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
