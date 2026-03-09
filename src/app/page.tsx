import Link from "next/link";

export default function HomePage() {
  return (
    <section className="space-y-8">
      <div className="card p-8 bg-gradient-to-r from-indigo-50 via-white to-violet-50">
        <h1 className="text-3xl font-bold tracking-tight">Skill-Bridge Career Navigator</h1>
        <p className="mt-3 text-slate-600 max-w-3xl">
          Get a personalized roadmap from your current skill set to your target role. Inspired by strong job/career UX patterns while staying focused on fast, actionable learning plans.
        </p>
        <div className="mt-6 flex gap-3">
          <Link className="btn-primary" href="/profiles/new">Start with Profile</Link>
          <Link className="btn border border-slate-300 hover:bg-slate-100" href="/search">Browse Roles & Courses</Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card p-5">
          <h2 className="font-semibold">1) Build Profile</h2>
          <p className="text-sm text-slate-600 mt-2">Add current skills, target role, time, and budget constraints.</p>
        </div>
        <div className="card p-5">
          <h2 className="font-semibold">2) Analyze Gaps</h2>
          <p className="text-sm text-slate-600 mt-2">Compare against synthetic job data for missing required skills.</p>
        </div>
        <div className="card p-5">
          <h2 className="font-semibold">3) Execute Roadmap</h2>
          <p className="text-sm text-slate-600 mt-2">Receive phased learning steps with estimated hours and resources.</p>
        </div>
      </div>
    </section>
  );
}
