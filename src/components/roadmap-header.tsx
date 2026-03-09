import React from "react";

type RoadmapHeaderProps = {
  title: string;
  summary: string;
  generationMode: "ai" | "fallback";
  generationNotes: string;
};

export function RoadmapHeader({ title, summary, generationMode, generationNotes }: RoadmapHeaderProps) {
  const isAI = generationMode === "ai";

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{title}</h1>
          <p className="text-slate-600 mt-1">{summary}</p>
        </div>
        <span className={`badge ${isAI ? "bg-emerald-100 text-emerald-700" : "bg-amber-100 text-amber-700"}`}>
          {isAI ? "AI Generated" : "Fallback Planner"}
        </span>
      </div>

      {!isAI && (
        <p className="mt-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3" role="status" aria-live="polite">
          AI was unavailable. A deterministic fallback roadmap was generated. {generationNotes}
        </p>
      )}
    </div>
  );
}
