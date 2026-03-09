"use client";

import { searchCourses, searchJobs } from "@/lib/api";
import { Course, Job } from "@/lib/types";
import { useEffect, useState } from "react";

export default function SearchPage() {
  const [skill, setSkill] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        setLoading(true);
        setError("");
        const params = new URLSearchParams();
        if (skill) params.set("skill", skill);
        const [jobsData, coursesData] = await Promise.all([searchJobs(params), searchCourses(params)]);
        setJobs(jobsData);
        setCourses(coursesData);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Unable to search");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [skill]);

  return (
    <section className="space-y-6">
      <div className="card p-5">
        <h1 className="text-2xl font-semibold">Market Explorer</h1>
        <p className="text-slate-600 mt-1">Filter synthetic job and learning data by skill.</p>
        <div className="mt-4">
          <input
            className="input max-w-md"
            placeholder="Try: Python, AWS, SQL"
            value={skill}
            onChange={(e) => setSkill(e.target.value)}
          />
        </div>
      </div>

      {error && <p className="text-red-700 bg-red-50 border border-red-200 p-3 rounded-lg">{error}</p>}
      {loading && <p className="text-slate-600">Loading market data...</p>}

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card p-5">
          <h2 className="font-semibold">Jobs ({jobs.length})</h2>
          <div className="mt-3 space-y-3">
            {jobs.map((job) => (
              <div key={job.id} className="rounded-xl border border-slate-200 p-3">
                <p className="font-medium">{job.title}</p>
                <p className="text-sm text-slate-600">{job.company} • {job.remote_type}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {job.required_skills.slice(0, 4).map((s) => (
                    <span className="badge bg-indigo-100 text-indigo-700" key={s}>{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-5">
          <h2 className="font-semibold">Courses ({courses.length})</h2>
          <div className="mt-3 space-y-3">
            {courses.map((course) => (
              <div key={course.id} className="rounded-xl border border-slate-200 p-3">
                <p className="font-medium">{course.title}</p>
                <p className="text-sm text-slate-600">{course.provider} • ${course.cost_amount}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {course.skills_covered.slice(0, 4).map((s) => (
                    <span className="badge bg-violet-100 text-violet-700" key={s}>{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
