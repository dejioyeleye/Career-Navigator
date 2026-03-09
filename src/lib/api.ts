import {
  AnalyticsSummary,
  Course,
  InterviewQuestions,
  Job,
  ProfileScorecard,
  ResumeImportResult,
  Roadmap,
  RoadmapSummary,
  TransferableSkills,
  UserProfile,
} from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_BASE_FALLBACK = API_BASE.includes("localhost") ? API_BASE.replace("localhost", "127.0.0.1") : null;

async function doFetch(path: string, options?: RequestInit, base?: string): Promise<Response> {
  return fetch(`${base ?? API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    cache: "no-store",
  });
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await doFetch(path, options);
  } catch (err) {
    if (API_BASE_FALLBACK) {
      response = await doFetch(path, options, API_BASE_FALLBACK);
    } else {
      throw err;
    }
  }
  if (!response.ok) {
    let errorMessage = "Request failed";
    try {
      const json = await response.json();
      errorMessage = json?.detail?.message ?? json?.message ?? errorMessage;
    } catch {
      // ignore parsing error
    }
    throw new Error(errorMessage);
  }
  return response.json();
}

export async function importResumeFile(file: File): Promise<ResumeImportResult> {
  const formData = new FormData();
  formData.append("file", file);

  const send = async (base: string) =>
    fetch(`${base}/api/profiles/import`, {
      method: "POST",
      body: formData,
      cache: "no-store",
    });

  let response: Response;
  try {
    response = await send(API_BASE);
  } catch (err) {
    if (API_BASE_FALLBACK) {
      response = await send(API_BASE_FALLBACK);
    } else {
      throw err;
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Failed to parse resume" }));
    throw new Error(errorData.detail || "Failed to parse resume");
  }

  return response.json();
}

export async function createProfile(payload: Omit<UserProfile, "id">): Promise<UserProfile> {
  return request<UserProfile>("/api/profiles", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getProfile(id: number): Promise<UserProfile> {
  return request<UserProfile>(`/api/profiles/${id}`);
}

export async function updateProfile(id: number, payload: Partial<UserProfile>): Promise<UserProfile> {
  return request<UserProfile>(`/api/profiles/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function getProfileScorecard(id: number): Promise<ProfileScorecard> {
  return request<ProfileScorecard>(`/api/profiles/${id}/scorecard`);
}

export async function searchJobs(params: URLSearchParams): Promise<Job[]> {
  return request<Job[]>(`/api/search/jobs?${params.toString()}`);
}

export async function searchCourses(params: URLSearchParams): Promise<Course[]> {
  return request<Course[]>(`/api/search/courses?${params.toString()}`);
}

export async function generateRoadmap(user_profile_id: number, target_job_id?: number): Promise<Roadmap> {
  return request<Roadmap>("/api/roadmaps", {
    method: "POST",
    body: JSON.stringify({ user_profile_id, target_job_id }),
  });
}

export async function getRoadmap(id: number): Promise<Roadmap> {
  return request<Roadmap>(`/api/roadmaps/${id}`);
}

export async function listRoadmaps(user_profile_id: number): Promise<RoadmapSummary[]> {
  return request<RoadmapSummary[]>(`/api/roadmaps?user_profile_id=${user_profile_id}`);
}

export async function updateRoadmapSteps(
  id: number,
  steps: Array<{ id: number; completed: boolean }>
): Promise<Roadmap> {
  return request<Roadmap>(`/api/roadmaps/${id}/steps`, {
    method: "PUT",
    body: JSON.stringify({ steps }),
  });
}

export async function importResume(payload: {
  full_name?: string;
  email?: string;
  current_role?: string;
  target_role?: string;
  location?: string;
  years_experience?: number;
  skills?: string[];
}): Promise<ResumeImportResult> {
  return request<ResumeImportResult>("/api/profiles/import", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getTransferableSkills(profile_id: number): Promise<TransferableSkills> {
  return request<TransferableSkills>(`/api/profiles/${profile_id}/transferable-skills`);
}

export async function getAnalytics(profile_id: number): Promise<AnalyticsSummary> {
  return request<AnalyticsSummary>(`/api/profiles/${profile_id}/analytics`);
}

export async function generateInterviewQuestions(
  user_profile_id: number,
  target_job_id?: number
): Promise<InterviewQuestions> {
  return request<InterviewQuestions>("/api/interviews/questions", {
    method: "POST",
    body: JSON.stringify({ user_profile_id, target_job_id }),
  });
}

export async function getMentorSnapshot(profile_id: number): Promise<{
  profile: UserProfile;
  roadmaps: RoadmapSummary[];
}> {
  return request(`/api/mentor/snapshot/${profile_id}`);
}
