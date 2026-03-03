"use client";

import { useState } from "react";
import { Navigation } from "@/components/layout/Navigation";
import { GlobalDrawer } from "@/components/layout/GlobalDrawer";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { DemoSection } from "@/components/landing/DemoSection";
import { Features } from "@/components/landing/Features";
import { MemePreview } from "@/components/landing/MemePreview";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { FloatingButtons } from "@/components/landing/FloatingButtons";

export default function HomePage() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation onMenuClick={() => setDrawerOpen(true)} />
      <GlobalDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />
      <Hero />
      <DemoSection />
      <Features />
      <HowItWorks />
      <MemePreview />
      <FinalCTA />
      <FloatingButtons />
    </div>
  );
}
