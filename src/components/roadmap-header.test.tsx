import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import React from "react";

import { RoadmapHeader } from "@/components/roadmap-header";

describe("RoadmapHeader", () => {
  it("renders fallback notice when generation mode is fallback", () => {
    render(
      <RoadmapHeader
        title="Cloud Engineer Readiness"
        summary="Focus on AWS and Terraform"
        generationMode="fallback"
        generationNotes="Timeout from AI provider"
      />,
    );

    expect(screen.getByText("Fallback Planner")).toBeInTheDocument();
    expect(screen.getByText(/AI was unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/Timeout from AI provider/i)).toBeInTheDocument();
  });
});
