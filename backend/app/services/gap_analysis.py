from __future__ import annotations

from .taxonomy import canonicalize_skills


def normalized(items: list[str]) -> list[str]:
    return canonicalize_skills(items)


def calculate_gap(user_skills: list[str], required: list[str], preferred: list[str]) -> dict:
    user = set(normalized(user_skills))
    req = set(normalized(required))
    pref = set(normalized(preferred))

    strengths = sorted(user.intersection(req.union(pref)))
    missing_required = sorted(req.difference(user))
    missing_preferred = sorted(pref.difference(user))

    required_coverage = 1.0 if len(req) == 0 else len(req.intersection(user)) / len(req)
    preferred_coverage = 1.0 if len(pref) == 0 else len(pref.intersection(user)) / len(pref)
    match_score = round((required_coverage * 0.75) + (preferred_coverage * 0.25), 3)

    return {
        "strengths": strengths,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "required_coverage": round(required_coverage, 3),
        "preferred_coverage": round(preferred_coverage, 3),
        "match_score": match_score,
    }


def score_job_fit(
    *,
    user_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
    target_role: str,
    job_title: str,
    years_experience: float,
    experience_level: str,
) -> float:
    user = set(normalized(user_skills))
    req = set(normalized(required_skills))
    pref = set(normalized(preferred_skills))

    required_coverage = 1.0 if len(req) == 0 else len(req.intersection(user)) / len(req)
    preferred_coverage = 1.0 if len(pref) == 0 else len(pref.intersection(user)) / len(pref)

    target_tokens = set(normalized(target_role.replace("/", " ").replace("-", " ").split()))
    title_tokens = set(normalized(job_title.replace("/", " ").replace("-", " ").split()))
    role_alignment = 0.0 if len(target_tokens) == 0 else len(target_tokens.intersection(title_tokens)) / len(target_tokens)

    expected_experience = {"junior": 1.0, "mid": 3.0, "senior": 6.0}.get(experience_level.lower(), 2.0)
    exp_delta = abs(float(years_experience) - expected_experience)
    experience_fit = max(0.0, 1 - (exp_delta / 6))

    score = (required_coverage * 0.55) + (preferred_coverage * 0.2) + (role_alignment * 0.15) + (experience_fit * 0.1)
    return round(score, 3)
