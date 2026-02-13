"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their original state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join our competitive basketball team and participate in local tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu"]
        },
        "Art Club": {
            "description": "Express creativity through painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu", "noah@mergington.edu"]
        },
        "Theater Production": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Thursdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 16,
            "participants": ["luke@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific concepts through experiments and STEM projects",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current activities
    activities.clear()
    # Add back the original activities
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_list(self, client, reset_activities):
        """Test that /activities returns a list of all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """Test that Chess Club is in the activities list"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert data["Chess Club"]["max_participants"] == 12
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for a non-existent activity"""
        response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        # Sign up the first time
        response1 = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response1.status_code == 200
        
        # Try to sign up again
        response2 = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Student already signed up"
    
    def test_signup_already_registered_student(self, client, reset_activities):
        """Test that an already registered student cannot sign up again"""
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]


class TestUnregisterForActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successfully unregistering from an activity"""
        response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from a non-existent activity"""
        response = client.delete("/activities/Nonexistent Club/signup?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test unregistering a student who is not registered"""
        response = client.delete("/activities/Chess Club/signup?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_and_signup_again(self, client, reset_activities):
        """Test that a student can sign up after unregistering"""
        # Unregister
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        
        # Sign up again
        response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        
        # Verify participant is back
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
