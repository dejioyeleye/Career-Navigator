"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function ResumeImportPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        setError("Only PDF files are accepted");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError("");
      setPreview(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError("Please select a PDF file");
      return;
    }

    try {
      setError("");
      setLoading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/profiles/import', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Import failed');
      }
      
      const result = await response.json();
      setPreview(result.mapped_profile);
      
      // Show preview first, then user can create profile
    } catch (err) {
      setError(err instanceof Error ? err.message : "Import failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="max-w-4xl mx-auto space-y-6">
      <div className="card p-6">
        <h1 className="text-2xl font-semibold">Import Resume Data</h1>
        <p className="text-slate-600 mt-2">
          Paste your resume JSON or upload structured data to quickly create your profile.
        </p>
      </div>

      <div className="card p-6 space-y-4">
        <div>
          <label className="text-sm font-medium">Upload Resume (PDF only)</label>
          <input
            type="file"
            accept=".pdf"
            className="block w-full mt-1 text-sm text-slate-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-lg file:border-0
              file:text-sm file:font-semibold
              file:bg-indigo-50 file:text-indigo-700
              hover:file:bg-indigo-100
              cursor-pointer"
            onChange={handleFileChange}
          />
          <p className="text-xs text-slate-500 mt-1">
            Upload your resume in PDF format. We'll extract your skills and basic information.
          </p>
          {file && (
            <p className="text-sm text-green-700 mt-2">
              ✓ Selected: {file.name}
            </p>
          )}
        </div>

        {error && (
          <div className="rounded-lg bg-red-50 text-red-700 p-3 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="button"
            onClick={handleImport}
            className="btn-primary"
            disabled={!file || loading}
          >
            {loading ? "Processing PDF..." : "Parse Resume"}
          </button>
          {preview && (
            <Link 
              href="/profiles/new" 
              className="btn-primary"
            >
              Create Profile with Extracted Data
            </Link>
          )}
          <Link href="/profiles/new" className="btn-secondary">
            Cancel
          </Link>
        </div>
      </div>

      {preview && (
        <div className="card p-6">
          <h2 className="font-semibold mb-4">Preview Extracted Data</h2>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-500">Name:</span>
              <p className="font-medium">{preview.full_name || preview.name || "—"}</p>
            </div>
            <div>
              <span className="text-slate-500">Email:</span>
              <p className="font-medium">{preview.email || "—"}</p>
            </div>
            <div>
              <span className="text-slate-500">Current Role:</span>
              <p className="font-medium">{preview.current_role || "—"}</p>
            </div>
            <div>
              <span className="text-slate-500">Target Role:</span>
              <p className="font-medium">{preview.target_role || "—"}</p>
            </div>
            <div>
              <span className="text-slate-500">Location:</span>
              <p className="font-medium">{preview.location || "—"}</p>
            </div>
            <div>
              <span className="text-slate-500">Experience:</span>
              <p className="font-medium">{preview.years_experience || 0} years</p>
            </div>
          </div>
          {preview.skills && preview.skills.length > 0 && (
            <div className="mt-4">
              <span className="text-slate-500 text-sm">Skills:</span>
              <div className="mt-2 flex flex-wrap gap-2">
                {preview.skills.map((skill: string, i: number) => (
                  <span key={i} className="badge bg-indigo-100 text-indigo-700">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
