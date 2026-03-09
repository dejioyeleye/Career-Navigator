"use client";

import { Roadmap } from "@/lib/types";
import { updateRoadmapSteps } from "@/lib/api";
import { useState } from "react";

export function RoadmapStepEditor({ roadmap }: { roadmap: Roadmap }) {
  const [steps, setSteps] = useState(roadmap.steps);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleToggle = async (stepOrder: number) => {
    const updatedSteps = steps.map((s) =>
      s.order === stepOrder ? { ...s, completed: !s.completed } : s
    );
    setSteps(updatedSteps);

    try {
      setSaving(true);
      setMessage("");
      await updateRoadmapSteps(
        roadmap.id,
        updatedSteps.map((s) => ({ id: s.order, completed: s.completed || false }))
      );
      setMessage("✓ Saved");
      setTimeout(() => setMessage(""), 2000);
    } catch (err) {
      setMessage("Failed to save");
      // Revert on error
      setSteps(steps);
    } finally {
      setSaving(false);
    }
  };

  const completedCount = steps.filter((s) => s.completed).length;
  const progressPct = Math.round((completedCount / steps.length) * 100);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">Roadmap Progress</h2>
        <div className="flex items-center gap-3">
          {message && <span className="text-sm text-green-600">{message}</span>}
          <span className="text-sm text-slate-600">
            {completedCount} of {steps.length} completed ({progressPct}%)
          </span>
        </div>
      </div>

      <div className="bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-indigo-500 transition-all duration-300"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div
            key={step.order}
            className="flex items-start gap-3 p-4 border border-slate-200 rounded-lg hover:border-indigo-300 transition"
          >
            <input
              type="checkbox"
              checked={step.completed || false}
              onChange={() => handleToggle(step.order)}
              disabled={saving}
              className="mt-1 h-5 w-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
            />
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <span className="font-medium text-slate-900">{step.goal}</span>
                <span className="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600">
                  Step {step.order}
                </span>
              </div>
              <p className="text-sm text-slate-600 mt-1">
                {step.estimate_hours} hours • {step.skill_focus.length} skills
              </p>
              {step.rationale && (
                <p className="text-xs text-slate-500 mt-2 italic">💡 {step.rationale}</p>
              )}

              {step.recommended_courses && step.recommended_courses.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {step.recommended_courses.slice(0, 4).map((course) => (
                    <a
                      key={`${step.order}-${course.title}-${course.url}`}
                      href={course.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700"
                    >
                      Open course: {course.title}
                    </a>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
