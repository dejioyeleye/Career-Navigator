from __future__ import annotations

from collections import defaultdict


def build_fallback_roadmap(gap: dict, courses: list[dict], audience_mode: str | None = None) -> tuple[str, list[dict], str]:
    missing = gap.get("missing_required_skills", []) + gap.get("missing_preferred_skills", [])
    by_skill: dict[str, list[dict]] = defaultdict(list)

    for course in courses:
        for skill in course.get("skills_covered", []):
            by_skill[skill.strip().lower()].append(course)

    steps: list[dict] = []
    order = 1
    for skill in missing[:6]:
        options = by_skill.get(skill.lower(), [])
        if audience_mode == "recent_graduate":
            options = sorted(options, key=lambda c: (0 if c.get("is_certificate") else 1, c.get("cost_amount", 999999), c.get("duration_hours", 999999)))[:2]
        else:
            options = sorted(options, key=lambda c: (c.get("cost_amount", 999999), c.get("duration_hours", 999999)))[:2]

        steps.append(
            {
                "order": order,
                "goal": f"Build practical competency in {skill.title()}",
                "skill_focus": [skill],
                "recommended_course_ids": [o["id"] for o in options],
                "recommended_courses": [
                    {
                        "title": o.get("title", "Course"),
                        "url": o.get("url", ""),
                        "provider": o.get("provider"),
                        "cost_amount": o.get("cost_amount"),
                        "cost_currency": o.get("cost_currency", "USD"),
                        "skills_learned": o.get("skills_covered", []),
                        "duration_hours": o.get("duration_hours"),
                        "why_this_course": f"Targets missing skill: {skill}",
                    }
                    for o in options[:4]
                ],
                "estimate_hours": round(sum(o.get("duration_hours", 0) for o in options) or 6, 1),
                "rationale": f"{skill.title()} appears as a gap in target-role requirements.",
                "evidence": [f"Missing target skill: {skill}", f"Mapped {len(options)} relevant learning resources"],
                "confidence": 0.72,
            }
        )
        order += 1

    if audience_mode == "career_switcher":
        steps.insert(
            0,
            {
                "order": 0,
                "goal": "Map transferable skills from your current background",
                "skill_focus": gap.get("strengths", [])[:3] or ["communication", "problem solving"],
                "recommended_course_ids": [],
                "recommended_courses": [],
                "estimate_hours": 3.0,
                "rationale": "Career-switcher path starts with explicit transferability framing.",
                "evidence": ["Transferable strengths were identified from your existing skill set"],
                "confidence": 0.68,
            },
        )
        for index, step in enumerate(steps, start=1):
            step["order"] = index

    if not steps:
        steps = [
            {
                "order": 1,
                "goal": "Strengthen portfolio with one end-to-end project",
                "skill_focus": ["system design", "communication"],
                "recommended_course_ids": [],
                "recommended_courses": [],
                "estimate_hours": 8.0,
                "rationale": "Portfolio evidence improves hiring signal across entry-level roles.",
                "evidence": ["No major gaps found; focus shifts to differentiation"],
                "confidence": 0.65,
            }
        ]

    summary = "Your roadmap prioritizes missing required skills first, then preferred differentiators."
    if audience_mode == "recent_graduate":
        summary = "Your roadmap prioritizes missing skills and certificate-oriented milestones for entry-level competitiveness."
    elif audience_mode == "career_switcher":
        summary = "Your roadmap emphasizes transferable strengths first, then closes domain-specific technical gaps."

    notes = "Generated using deterministic fallback planner."
    return summary, steps, notes
