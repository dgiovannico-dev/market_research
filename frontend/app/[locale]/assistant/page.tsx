"use client";

import { DemandCompassSection } from "@/widgets/demand-compass";
import { ProposeSection } from "@/widgets/propose";

export default function AssistantPage() {
  return (
    <div className="space-y-6 text-[var(--ink)]">
      <DemandCompassSection />
      <ProposeSection />
    </div>
  );
}
