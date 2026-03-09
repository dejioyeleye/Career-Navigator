from __future__ import annotations


def build_mvp_static_roadmap() -> tuple[str, list[dict], str]:
    courses = [
        {
            "order": 1,
            "name": "Python for Data Science, AI & Development",
            "url": "https://www.coursera.org/learn/python-for-applied-data-science-ai",
            "provider": "IBM via Coursera",
            "level": "Beginner",
            "duration_hours": 25,
            "time_to_complete_weeks": 4,
            "cost_amount": 0,
            "cost_currency": "USD",
            "skills_learned": ["Python", "Pandas", "NumPy", "Data Visualization"],
            "prerequisites": ["Basic Programming"],
            "project_included": True,
            "certificate": True,
            "ml_focus": "supervised",
            "why_recommended": "A necessary refresh on Python libraries essential for data manipulation before building ML models.",
            "outcome": "You will be able to clean, transform, and visualize datasets using standard Python data science tools.",
            "fit_score": 95,
        },
        {
            "order": 2,
            "name": "Supervised Machine Learning: Regression and Classification",
            "url": "https://www.coursera.org/learn/machine-learning",
            "provider": "DeepLearning.AI / Stanford",
            "level": "Beginner",
            "duration_hours": 33,
            "time_to_complete_weeks": 3,
            "cost_amount": 49,
            "cost_currency": "USD",
            "skills_learned": ["Linear Regression", "Logistic Regression", "Scikit-Learn", "Gradient Descent"],
            "prerequisites": ["Python Data Science Libraries", "High School Math"],
            "project_included": True,
            "certificate": True,
            "ml_focus": "supervised",
            "why_recommended": "The industry standard introduction to core ML concepts by Andrew Ng, bridging the gap from SE to ML.",
            "outcome": "You will build, train, and evaluate classical supervised machine learning models.",
            "fit_score": 98,
        },
        {
            "order": 3,
            "name": "Neural Networks and Deep Learning",
            "url": "https://www.coursera.org/learn/neural-networks-deep-learning",
            "provider": "DeepLearning.AI",
            "level": "Intermediate",
            "duration_hours": 24,
            "time_to_complete_weeks": 4,
            "cost_amount": 49,
            "cost_currency": "USD",
            "skills_learned": ["Neural Networks", "Backpropagation", "TensorFlow", "Vectorization"],
            "prerequisites": ["Python", "Supervised ML Basics", "Linear Algebra"],
            "project_included": True,
            "certificate": True,
            "ml_focus": "deep_learning",
            "why_recommended": "Provides the mathematical and practical foundation for modern deep learning architectures and deep neural nets.",
            "outcome": "You will build a deep neural network from scratch and implement vectorized computations.",
            "fit_score": 96,
        },
        {
            "order": 4,
            "name": "Generative AI with Large Language Models",
            "url": "https://www.coursera.org/learn/generative-ai-with-llms",
            "provider": "DeepLearning.AI / AWS",
            "level": "Intermediate",
            "duration_hours": 16,
            "time_to_complete_weeks": 3,
            "cost_amount": 49,
            "cost_currency": "USD",
            "skills_learned": ["LLM Architecture", "Fine-Tuning", "Prompt Engineering", "PEFT"],
            "prerequisites": ["Python", "Deep Learning Fundamentals"],
            "project_included": True,
            "certificate": True,
            "ml_focus": "llm",
            "why_recommended": "A highly practical course bridging traditional deep learning with modern generative AI and LLM engineering tasks.",
            "outcome": "You will evaluate, fine-tune, and optimize a large language model for a domain-specific use case.",
            "fit_score": 97,
        },
    ]

    steps = [
        {
            "order": c["order"],
            "goal": f"Complete: {c['name']}",
            "skill_focus": c["skills_learned"][:3],
            "recommended_course_ids": [],
            "recommended_courses": [
                {
                    "title": c["name"],
                    "url": c["url"],
                    "provider": c["provider"],
                    "cost_amount": c["cost_amount"],
                    "cost_currency": c["cost_currency"],
                    "skills_learned": c["skills_learned"],
                    "duration_hours": c["duration_hours"],
                    "why_this_course": c["why_recommended"],
                }
            ],
            "estimate_hours": float(c["duration_hours"]),
            "rationale": c["why_recommended"],
            "evidence": [c["outcome"], f"Fit score: {c['fit_score']}"],
            "confidence": min(max(c["fit_score"] / 100, 0.0), 1.0),
        }
        for c in courses
    ]

    summary = "Software Engineer to ML/AI Transition Track with 4 recommendations."
    notes = "Generated using static MVP recommendation set."
    return summary, steps, notes
