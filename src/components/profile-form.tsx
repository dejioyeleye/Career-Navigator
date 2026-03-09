"use client";

import { createProfile, generateRoadmap, importResumeFile } from "@/lib/api";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const schema = z.object({
  full_name: z.string().min(2),
  email: z.string().email(),
  current_role: z.string().min(2),
  target_role: z.string().min(2),
  years_experience: z.coerce.number().min(0).max(40),
  location: z.string().min(2),
  skills_current: z.string().min(2),
  skills_target: z.string().optional().default(""),
  learning_preferences: z.string().optional().default(""),
  weekly_hours_available: z.coerce.number().min(1).max(60),
  budget_limit: z.coerce.number().min(0),
  audience_mode: z.enum(["recent_graduate", "career_switcher", "mentor"]).optional(),
});

type FormValues = z.infer<typeof schema>;

export function ProfileForm() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const { register, handleSubmit, formState: { errors }, setValue } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      skills_current: "Python, SQL",
      skills_target: "",
      learning_preferences: "self-paced, project-based",
      years_experience: 1,
      weekly_hours_available: 8,
      budget_limit: 100,
      location: "Remote",
      audience_mode: undefined,
    }
  });

  const handleResumeUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError("Only PDF files are accepted");
      return;
    }

    try {
      setUploadError("");
      setUploading(true);

      const result = await importResumeFile(file);
      const profile = result.mapped_profile;
      const skills = result.extracted_skills || [];
      
      // Autofill form fields
      if (profile.full_name) setValue('full_name', profile.full_name);
      if (profile.email) setValue('email', profile.email);
      if (profile.current_role) setValue('current_role', profile.current_role);
      if (profile.target_role) setValue('target_role', profile.target_role);
      if (profile.location) setValue('location', profile.location);
      if (profile.years_experience) setValue('years_experience', profile.years_experience);
      if (skills.length > 0) setValue('skills_current', skills.join(', '));
      
      // Show success message
      setUploadSuccess(true);
      setTimeout(() => {
        setUploadSuccess(false);
      }, 5000);
      
    } catch (err) {
      console.error("Resume upload error:", err);
      setUploadError(err instanceof Error ? err.message : "Failed to parse resume");
    } finally {
      setUploading(false);
    }
  };

  const onSubmit = async (values: FormValues) => {
    try {
      setServerError("");
      setIsSubmitting(true);
      
      // Build learning preferences array, including audience mode if selected
      const prefs = values.learning_preferences.split(",").map((s) => s.trim()).filter(Boolean);
      if (values.audience_mode) {
        prefs.push(`audience:${values.audience_mode}`);
      }
      
      const profile = await createProfile({
        full_name: values.full_name,
        email: values.email,
        current_role: values.current_role,
        target_role: values.target_role,
        years_experience: values.years_experience,
        location: values.location,
        skills_current: values.skills_current.split(",").map((s) => s.trim()).filter(Boolean),
        skills_target: values.skills_target.split(",").map((s) => s.trim()).filter(Boolean),
        learning_preferences: prefs,
        weekly_hours_available: values.weekly_hours_available,
        budget_limit: values.budget_limit,
      });

      const roadmap = await generateRoadmap(profile.id);
      router.push(`/roadmaps/${roadmap.id}?profile=${profile.id}`);
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Unable to save profile");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Resume Upload Section */}
      <div className="card p-5 bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
        <div className="flex items-start gap-4">
          <div className="text-3xl">📄</div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-900">🚀 Quick Start: Upload Resume</h3>
            <p className="text-sm text-slate-600 mt-1">
              Upload your PDF resume and AI will auto-fill the form below
            </p>
            <div className="mt-3">
              <input
                type="file"
                accept=".pdf"
                onChange={handleResumeUpload}
                disabled={uploading}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-600 file:text-white
                  hover:file:bg-indigo-700
                  disabled:opacity-50
                  cursor-pointer"
              />
              {uploading && (
                <div className="mt-2 flex items-center gap-2 text-indigo-600">
                  <div className="animate-spin h-4 w-4 border-2 border-indigo-600 border-t-transparent rounded-full"></div>
                  <p className="text-sm">AI is analyzing your resume...</p>
                </div>
              )}
              {uploadSuccess && (
                <div className="mt-2 flex items-center gap-2 text-green-600 bg-green-50 p-2 rounded">
                  <span className="text-lg">✓</span>
                  <p className="text-sm font-medium">Resume parsed successfully! Form filled below.</p>
                </div>
              )}
              {uploadError && (
                <p className="text-sm text-red-600 mt-2 bg-red-50 p-2 rounded">
                  ❌ {uploadError}
                </p>
              )}
              {!uploading && !uploadError && !uploadSuccess && (
                <p className="text-xs text-slate-500 mt-2">
                  🔒 Secure: Max 5MB, processed with AI
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Create Career Profile</h1>
      {serverError && <p className="rounded-lg bg-red-50 text-red-700 p-3 text-sm">{serverError}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="text-sm font-medium">Full Name</label>
          <input className="input mt-1" {...register("full_name")} />
          {errors.full_name && <p className="text-sm text-red-600 mt-1">{errors.full_name.message}</p>}
        </div>
        <div>
          <label className="text-sm font-medium">Email</label>
          <input className="input mt-1" {...register("email")} />
          {errors.email && <p className="text-sm text-red-600 mt-1">{errors.email.message}</p>}
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="text-sm font-medium">Current Role</label>
          <input className="input mt-1" {...register("current_role")} />
        </div>
        <div>
          <label className="text-sm font-medium">Target Role</label>
          <input className="input mt-1" {...register("target_role")} />
        </div>
        <div>
          <label className="text-sm font-medium">Location</label>
          <input className="input mt-1" {...register("location")} />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div>
          <label className="text-sm font-medium">Years of Experience</label>
          <input type="number" step="0.5" className="input mt-1" {...register("years_experience")} />
        </div>
        <div>
          <label className="text-sm font-medium">Hours/Week</label>
          <input type="number" className="input mt-1" {...register("weekly_hours_available")} />
        </div>
        <div>
          <label className="text-sm font-medium">Budget (USD)</label>
          <input type="number" className="input mt-1" {...register("budget_limit")} />
        </div>
      </div>

      <div>
        <label className="text-sm font-medium">Current Skills (comma-separated)</label>
        <textarea className="input mt-1 min-h-20" {...register("skills_current")} />
      </div>

      <div>
        <label className="text-sm font-medium">Target Skills (optional)</label>
        <textarea className="input mt-1 min-h-20" {...register("skills_target")} />
      </div>

      <div>
        <label className="text-sm font-medium">Learning Preferences (optional)</label>
        <input className="input mt-1" {...register("learning_preferences")} />
      </div>

      <div>
        <label className="text-sm font-medium">I am a... (optional)</label>
        <select className="input mt-1" {...register("audience_mode")}>
          <option value="">Not specified</option>
          <option value="recent_graduate">🎓 Recent Graduate</option>
          <option value="career_switcher">🔄 Career Switcher</option>
          <option value="mentor">👨‍🏫 Mentor/Advisor</option>
        </select>
        <p className="text-xs text-slate-500 mt-1">
          This helps tailor roadmap recommendations to your background.
        </p>
      </div>

      <button disabled={isSubmitting} className="btn-primary disabled:opacity-50" type="submit">
        {isSubmitting ? "Generating roadmap..." : "Create Profile & Generate Roadmap"}
      </button>
    </form>
    </div>
  );
}
