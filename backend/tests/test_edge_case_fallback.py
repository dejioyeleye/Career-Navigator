from fastapi.testclient import TestClient

from app.main import app


def test_roadmap_fallback_when_ai_unavailable():
    with TestClient(app) as client:
        response = client.post("/api/roadmaps", json={"user_profile_id": 1})
        assert response.status_code == 200
        data = response.json()
        assert data["generation_mode"] == "fallback"
        assert "fallback" in data["generation_notes"].lower()


def test_validation_error_for_invalid_profile():
    with TestClient(app) as client:
        bad_payload = {
            "full_name": "A",
            "email": "invalid-email",
            "current_role": "X",
            "target_role": "Y",
            "years_experience": -1,
            "location": "R",
            "skills_current": [],
            "skills_target": [],
            "learning_preferences": [],
            "weekly_hours_available": 0,
            "budget_limit": -5,
        }
        response = client.post("/api/profiles", json=bad_payload)
        assert response.status_code == 422
