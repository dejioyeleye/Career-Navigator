from __future__ import annotations

import asyncio
import json
import logging
import re

from google import genai
from google.genai import types

from ..config import settings

logger = logging.getLogger(__name__)

# Configure Gemini client (reuse same pattern as gemini.py)
if settings.gemini_api_key:
    client = genai.Client(api_key=settings.gemini_api_key)
else:
    client = None


class AIServiceError(Exception):
    pass


def _parse_json_payload(raw_text: str) -> dict:
    text = (raw_text or "").strip()

    # Remove markdown fences when present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        if text.startswith("json"):
            text = text[4:].strip()

    # Candidate payloads: full text and best-effort { ... } extraction
    candidates = [text]
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(text[start : end + 1])

    last_error: Exception | None = None
    for candidate in candidates:
        for normalized in (
            candidate,
            re.sub(r",(\s*[}\]])", r"\1", candidate),
            re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", candidate),
        ):
            try:
                parsed = json.loads(normalized)
                if isinstance(parsed, dict):
                    return parsed
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue

    raise AIServiceError(f"Invalid JSON from Gemini: {last_error}")


def _repair_json_with_gemini(bad_json_text: str, model_name: str) -> dict:
    repair_prompt = (
        "Fix the following malformed JSON and return ONLY valid JSON with the same keys. "
        "Do not add explanations.\n\n"
        f"{bad_json_text}"
    )

    response = client.models.generate_content(
        model=model_name,
        contents=repair_prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=2200,
            response_mime_type="application/json",
        ),
    )
    return _parse_json_payload(response.text.strip())


def _normalized_model_name(name: str) -> str:
    return (name or "").replace("models/", "").strip()


def _model_candidates() -> list[str]:
    preferred = _normalized_model_name(settings.gemini_model)
    candidates = [
        preferred,
        "gemini-flash-lite-latest",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
        "gemini-flash-latest",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
    ]
    # Keep order, remove empties/duplicates
    seen: set[str] = set()
    out: list[str] = []
    for model in candidates:
        if model and model not in seen:
            seen.add(model)
            out.append(model)
    return out


def _safe_float(value: object, default: float) -> float:
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return default


def _normalize_url(value: object) -> str:
    if not isinstance(value, str):
        return ""
    out = value.strip()
    if not out:
        return ""
    if out.startswith("www."):
        out = f"https://{out}"
    if not out.startswith("http://") and not out.startswith("https://"):
        return ""
    return out


def _normalize_steps(steps: list[dict], courses: list[dict]) -> list[dict]:
    course_by_id = {int(c.get("id")): c for c in courses if c.get("id") is not None}
    normalized_steps: list[dict] = []

    for idx, raw_step in enumerate(steps):
        if not isinstance(raw_step, dict):
            continue

        order = int(_safe_float(raw_step.get("order"), idx + 1))
        goal = str(raw_step.get("goal") or f"Step {idx + 1}").strip()

        skill_focus_raw = raw_step.get("skill_focus", [])
        if isinstance(skill_focus_raw, str):
            skill_focus = [skill_focus_raw.strip()] if skill_focus_raw.strip() else []
        elif isinstance(skill_focus_raw, list):
            skill_focus = [str(s).strip() for s in skill_focus_raw if str(s).strip()]
        else:
            skill_focus = []

        recommended_course_ids: list[int] = []
        for cid in raw_step.get("recommended_course_ids", []) or []:
            try:
                recommended_course_ids.append(int(cid))
            except Exception:  # noqa: BLE001
                continue

        recommended_courses: list[dict] = []
        raw_courses = raw_step.get("recommended_courses", []) or []
        if isinstance(raw_courses, list):
            for c in raw_courses[:4]:
                if not isinstance(c, dict):
                    continue
                title = str(c.get("title") or "").strip()
                url = _normalize_url(c.get("url"))
                if not title or not url:
                    continue
                skills_learned_raw = c.get("skills_learned", [])
                if isinstance(skills_learned_raw, str):
                    skills_learned = [skills_learned_raw.strip()] if skills_learned_raw.strip() else []
                elif isinstance(skills_learned_raw, list):
                    skills_learned = [str(s).strip() for s in skills_learned_raw if str(s).strip()]
                else:
                    skills_learned = []
                recommended_courses.append(
                    {
                        "title": title,
                        "url": url,
                        "provider": str(c.get("provider") or "").strip() or None,
                        "cost_amount": _safe_float(c.get("cost_amount"), 0.0),
                        "cost_currency": str(c.get("cost_currency") or "USD"),
                        "skills_learned": skills_learned,
                        "duration_hours": _safe_float(c.get("duration_hours"), 0.0),
                        "why_this_course": str(c.get("why_this_course") or "").strip() or None,
                    }
                )

        # If AI did not provide rich courses, map from known course IDs
        if not recommended_courses and recommended_course_ids:
            for cid in recommended_course_ids[:4]:
                course = course_by_id.get(cid)
                if not course:
                    continue
                url = _normalize_url(course.get("url"))
                if not url:
                    continue
                recommended_courses.append(
                    {
                        "title": str(course.get("title") or "Course"),
                        "url": url,
                        "provider": str(course.get("provider") or "").strip() or None,
                        "cost_amount": _safe_float(course.get("cost_amount"), 0.0),
                        "cost_currency": str(course.get("cost_currency") or "USD"),
                        "skills_learned": [str(s) for s in (course.get("skills_covered") or [])],
                        "duration_hours": _safe_float(course.get("duration_hours"), 0.0),
                        "why_this_course": "Mapped from curated catalog for this step",
                    }
                )

        estimate_hours = _safe_float(raw_step.get("estimate_hours"), 6.0)
        rationale = raw_step.get("rationale")

        evidence_raw = raw_step.get("evidence", [])
        if isinstance(evidence_raw, str):
            evidence = [evidence_raw.strip()] if evidence_raw.strip() else []
        elif isinstance(evidence_raw, list):
            evidence = [str(e).strip() for e in evidence_raw if str(e).strip()]
        else:
            evidence = []

        confidence = _safe_float(raw_step.get("confidence"), 0.72)
        if confidence > 1:
            confidence = confidence / 100
        confidence = max(0.0, min(1.0, confidence))

        normalized_steps.append(
            {
                "order": max(1, order),
                "goal": goal,
                "skill_focus": skill_focus,
                "recommended_course_ids": recommended_course_ids,
                "recommended_courses": recommended_courses,
                "estimate_hours": estimate_hours,
                "rationale": str(rationale).strip() if rationale else None,
                "evidence": evidence,
                "confidence": confidence,
            }
        )

    # Ensure stable ordering
    normalized_steps.sort(key=lambda s: s["order"])
    for i, step in enumerate(normalized_steps, start=1):
        step["order"] = i

    return normalized_steps


def _extract_summary_and_steps(parsed: dict, gap: dict) -> tuple[str, list[dict]]:
    summary = str(
        parsed.get("summary")
        or parsed.get("overview")
        or parsed.get("roadmap_summary")
        or "Personalized roadmap generated from your profile and target role."
    )

    steps = (
        parsed.get("steps")
        or parsed.get("roadmap_steps")
        or parsed.get("plan")
        or parsed.get("learning_path")
    )

    if isinstance(steps, dict):
        steps = steps.get("steps") or steps.get("items") or []

    if isinstance(steps, list) and steps:
        return summary, steps

    # Some responses provide courses without explicit steps. Convert to 4 steps.
    course_items = parsed.get("recommended_courses") or parsed.get("courses") or []
    if isinstance(course_items, list) and course_items:
        missing = (gap.get("missing_required_skills", []) + gap.get("missing_preferred_skills", [])) or ["career growth"]
        synthesized_steps: list[dict] = []
        for i, c in enumerate(course_items[:4], start=1):
            if not isinstance(c, dict):
                continue

            title = str(c.get("title") or c.get("name") or f"Recommended Course {i}")
            url = _normalize_url(c.get("url") or c.get("link") or c.get("course_url"))
            skills = c.get("skills_learned") or c.get("skills") or []
            if isinstance(skills, str):
                skills = [skills]
            if not isinstance(skills, list):
                skills = []

            synthesized_steps.append(
                {
                    "order": i,
                    "goal": f"Complete: {title}",
                    "skill_focus": [str(s).strip() for s in skills if str(s).strip()] or [missing[min(i - 1, len(missing) - 1)]],
                    "recommended_course_ids": [],
                    "recommended_courses": [
                        {
                            "title": title,
                            "url": url,
                            "provider": c.get("provider"),
                            "cost_amount": c.get("cost_amount") or c.get("cost") or 0,
                            "cost_currency": c.get("cost_currency") or "USD",
                            "skills_learned": [str(s).strip() for s in skills if str(s).strip()],
                            "duration_hours": c.get("duration_hours") or c.get("duration") or 6,
                            "why_this_course": c.get("why_this_course") or c.get("reason") or "Recommended by AI for your profile",
                        }
                    ],
                    "estimate_hours": c.get("duration_hours") or c.get("duration") or 6,
                    "rationale": "AI-selected course aligned with your target role and skill gaps.",
                    "evidence": [f"Complete {title}", "Add a project or certificate to portfolio"],
                    "confidence": 0.72,
                }
            )

        if synthesized_steps:
            return summary, synthesized_steps

    raise AIServiceError("AI response missing roadmap steps")


def _is_transient_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    transient_markers = [
        "timeout",
        "timed out",
        "deadline",
        "request timeout",
        "429",
        "503",
        "temporarily unavailable",
        "unavailable",
    ]
    return any(marker in msg for marker in transient_markers)


def _select_course_candidates(courses: list[dict], gap: dict, budget_limit: float | None) -> list[dict]:
    missing = {str(s).strip().lower() for s in (gap.get("missing_required_skills", []) + gap.get("missing_preferred_skills", []))}

    def course_score(course: dict) -> tuple[int, float, float]:
        covered = {str(s).strip().lower() for s in course.get("skills_covered", [])}
        overlap = len(covered & missing)
        cost = float(course.get("cost_amount", 999999) or 999999)
        duration = float(course.get("duration_hours", 999999) or 999999)

        if budget_limit is not None and cost > budget_limit:
            overlap -= 1

        # higher overlap first, then cheaper, then shorter
        return (-overlap, cost, duration)

    ranked = sorted(courses, key=course_score)
    shortlisted = ranked[:8]

    # keep only fields needed by model to reduce prompt size and timeouts
    compact = []
    for c in shortlisted:
        compact.append(
            {
                "id": c.get("id"),
                "title": c.get("title"),
                "provider": c.get("provider"),
                "url": c.get("url"),
                "cost_amount": c.get("cost_amount"),
                "cost_currency": c.get("cost_currency", "USD"),
                "duration_hours": c.get("duration_hours"),
                "skills_covered": c.get("skills_covered", []),
                "is_certificate": bool(c.get("is_certificate", False)),
            }
        )
    return compact


async def generate_ai_roadmap(profile: dict, job: dict, courses: list[dict], gap: dict, audience_mode: str | None = None) -> tuple[str, list[dict], str]:
    if not client:
        raise AIServiceError("Missing API key")
    
    budget_limit = profile.get("budget_limit") if isinstance(profile, dict) else None
    selected_courses = _select_course_candidates(courses, gap, budget_limit)

    prompt = f"""You are a career roadmap planner. Analyze the following data and return ONLY a valid JSON object (no markdown, no code blocks).

Profile: {json.dumps(profile)}
Target Job: {json.dumps(job)}
Skill Gap: {json.dumps(gap)}
Audience Mode: {audience_mode}
Available Courses: {json.dumps(selected_courses)}

Return strict JSON with these exact keys:
- summary (string): Brief overview of the learning path
- steps (array): Each step must have:
  - order (number): Step number starting from 1
  - goal (string): What to achieve
    - skill_focus (array of strings): Primary skills to develop
    - recommended_course_ids (array of numbers): Optional course IDs from the provided list
    - recommended_courses (array of exactly 4 objects): include title, url, provider, cost_amount, cost_currency, skills_learned (array), duration_hours, why_this_course
  - estimate_hours (number): Hours needed
  - rationale (string): Why this step matters
    - evidence (array of strings): How to prove competency
    - confidence (number): 0.0 to 1.0 confidence score

Important:
- URLs must be full links starting with https://
- Keep JSON valid and properly escaped
- Recommend practical courses aligned to the skill gap and budget

Return ONLY the JSON object, no additional text."""

    try:
        response = None
        last_error: Exception | None = None
        selected_model: str | None = None

        for model_name in _model_candidates():
            try:
                for attempt in range(2):
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                temperature=0.1,
                                max_output_tokens=1500,
                                top_p=0.9,
                                response_mime_type="application/json",
                            )
                        )
                        selected_model = model_name
                        break
                    except Exception as attempt_exc:  # noqa: BLE001
                        if _is_transient_error(attempt_exc) and attempt == 0:
                            await asyncio.sleep(0.8)
                            continue
                        raise
                if response is not None:
                    break
            except Exception as model_exc:  # noqa: BLE001
                msg = str(model_exc)
                if (
                    "NOT_FOUND" in msg
                    or "not found" in msg.lower()
                    or "RESOURCE_EXHAUSTED" in msg
                    or "quota" in msg.lower()
                    or "429" in msg
                ):
                    last_error = model_exc
                    continue
                raise

        if response is None:
            raise AIServiceError(f"No compatible Gemini model available. Last error: {last_error}")
        
        raw = response.text.strip()
        try:
            parsed = _parse_json_payload(raw)
        except AIServiceError:
            # One repair pass to recover from occasional malformed model JSON.
            if selected_model is None:
                raise
            parsed = _repair_json_with_gemini(raw, selected_model)
        summary, steps = _extract_summary_and_steps(parsed, gap)
        steps = _normalize_steps(steps, courses)
        return summary, steps, f"Generated with Gemini AI ({selected_model})."
    except Exception as exc:  # noqa: BLE001
        logger.error(f"Gemini roadmap generation failed: {str(exc)}")
        raise AIServiceError(str(exc)) from exc
