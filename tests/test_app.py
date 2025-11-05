"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
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
        },
        "Soccer Club": {
            "description": "Outdoor soccer practice and inter-school matches",
            "schedule": "Wednesdays and Saturdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Team practices, drills, and competitive games",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and mixed-media workshops",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stage production, and school performances",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["charlotte@mergington.edu", "jack@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, science fairs, and research projects",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "elijah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Debate practice, public speaking, and regional competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["harper@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that Chess Club has the correct structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "michael@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_full(self, client):
        """Test that signup fails when activity is at capacity"""
        # Fill up the Chess Club (max 12 participants)
        # It already has 2 participants, so add 10 more
        for i in range(10):
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
            assert response.status_code == 200
        
        # Now try to add one more (should fail)
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "overflow@mergington.edu"}
        )
        assert response.status_code == 400
        assert "Activity is full" in response.json()["detail"]
    
    def test_signup_case_insensitive_email(self, client):
        """Test that email matching is case-insensitive"""
        # Try to sign up with different case
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "MICHAEL@MERGINGTON.EDU"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_email_with_whitespace(self, client):
        """Test that emails with whitespace are normalized"""
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": "  newstudent@mergington.edu  "}
        )
        assert response.status_code == 200
        
        # Verify the email was stored in normalized form
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = [p.strip().lower() for p in activities_data["Programming Class"]["participants"]]
        assert "newstudent@mergington.edu" in participants


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = [p.lower() for p in activities_data["Chess Club"]["participants"]]
        assert "michael@mergington.edu" not in participants
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistration from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client):
        """Test unregistration when student is not registered"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_case_insensitive(self, client):
        """Test that unregistration is case-insensitive"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "MICHAEL@MERGINGTON.EDU"}
        )
        assert response.status_code == 200
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = [p.lower() for p in activities_data["Chess Club"]["participants"]]
        assert "michael@mergington.edu" not in participants
    
    def test_unregister_with_whitespace(self, client):
        """Test unregistration with email containing whitespace"""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "  michael@mergington.edu  "}
        )
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = [p.lower() for p in activities_data["Programming Class"]["participants"]]
        assert email in participants
        
        # Unregister
        unregister_response = client.post(
            "/activities/Programming Class/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistration
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = [p.lower() for p in activities_data["Programming Class"]["participants"]]
        assert email not in participants
    
    def test_multiple_activities_signup(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitasker@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        chess_participants = [p.lower() for p in activities_data["Chess Club"]["participants"]]
        assert email in chess_participants
        
        prog_participants = [p.lower() for p in activities_data["Programming Class"]["participants"]]
        assert email in prog_participants
