"""
Tests for the High School Management System API

Following the AAA (Arrange-Act-Assert) pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Art Studio", "Drama Club", "Science Olympiad", "Debate Team"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_contains_required_fields(self):
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Missing '{field}' in {activity_name}"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_participants = client.get("/activities").json()[activity_name]["participants"].copy()

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert "Signed up" in response.json()["message"]

    def test_signup_for_activity_adds_to_participants(self):
        # Arrange
        activity_name = "Programming Class"
        email = "teststudent@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1

    def test_signup_for_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_already_signed_up(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestRemoveSignup:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_remove_signup_success(self):
        # Arrange
        activity_name = "Tennis Club"
        email = "james@mergington.edu"  # Already signed up
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert "Removed" in response.json()["message"]

    def test_remove_signup_removes_from_participants(self):
        # Arrange
        activity_name = "Art Studio"
        email = "isabella@mergington.edu"  # Already signed up
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1

    def test_remove_signup_activity_not_found(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_signup_student_not_signed_up(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedupstudent@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]
