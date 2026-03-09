"use client";

import { InterviewQuestions } from "@/lib/types";
import { useEffect, useState } from "react";
import { generateInterviewQuestions } from "@/lib/api";

export function InterviewQuestionsCard({
  profileId,
  targetJobId,
}: {
  profileId: number;
  targetJobId?: number;
}) {
  const [questions, setQuestions] = useState<InterviewQuestions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    generateInterviewQuestions(profileId, targetJobId)
      .then(setQuestions)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [profileId, targetJobId]);

  if (loading) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">Generating interview questions...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-5">
        <p className="text-red-600">Failed to generate: {error}</p>
      </div>
    );
  }

  if (!questions || questions.questions.length === 0) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">No questions available yet.</p>
      </div>
    );
  }

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold">💬 Mock Interview Questions</h2>
        {questions.generation_mode === "fallback" && (
          <span className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">
            Basic
          </span>
        )}
      </div>

      <p className="text-sm text-slate-600 mb-4">
        Practice with these questions based on your target role and skills.
      </p>

      <div className="space-y-4">
        {questions.questions.map((q, idx) => (
          <div key={idx} className="border border-slate-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 h-6 w-6 rounded-full bg-indigo-100 text-indigo-700 text-xs font-medium grid place-items-center">
                {idx + 1}
              </span>
              <div className="flex-1">
                <p className="font-medium text-slate-900">{q.question}</p>
                {q.category && (
                  <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                    {q.category}
                  </span>
                )}
                {q.difficulty && (
                  <span
                    className={`inline-block mt-2 ml-2 text-xs px-2 py-0.5 rounded-full ${
                      q.difficulty === "easy"
                        ? "bg-green-100 text-green-700"
                        : q.difficulty === "medium"
                        ? "bg-amber-100 text-amber-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {q.difficulty}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {questions.notes && (
        <p className="text-xs text-slate-500 mt-4 italic">{questions.notes}</p>
      )}
    </div>
  );
}
