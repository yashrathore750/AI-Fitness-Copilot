from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_daily_analysis_pipeline(tmp_path: Path) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'fitness-test.db'}"

    with TestClient(create_app(database_url=database_url)) as client:
        user_response = client.post(
            "/users",
            json={
                "weight_kg": 78,
                "height_cm": 176,
                "goal": "fat_loss",
                "diet_type": "veg",
            },
        )
        assert user_response.status_code == 201
        user_id = user_response.json()["id"]

        for food_name in ["oats", "spinach"]:
            food_response = client.post(
                "/food-log",
                json={"user_id": user_id, "food_name": food_name, "servings": 1},
            )
            assert food_response.status_code == 201

        activity_response = client.post(
            "/activity",
            json={
                "user_id": user_id,
                "steps": 8000,
                "workout_type": "leg_day",
                "duration_minutes": 45,
            },
        )
        assert activity_response.status_code == 201

        analysis_response = client.get(f"/analysis/today?user_id={user_id}")
        assert analysis_response.status_code == 200

        payload = analysis_response.json()
        deficiency_names = {item["name"] for item in payload["deficiencies"]}

        assert "fiber" in deficiency_names
        assert "magnesium" in deficiency_names
        assert payload["nutrition_summary"]["calories_out"] > payload["nutrition_summary"]["calories_in"]
        assert payload["insights"]["summary"].startswith("You maintained a calorie deficit")
        assert payload["insights"]["suggestions"]