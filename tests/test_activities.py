"""Tests for the GET /activities endpoint."""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that the endpoint returns all activities.
    
    AAA Pattern:
    - Arrange: TestClient is ready (from fixture)
    - Act: Make GET request to /activities
    - Assert: Response is 200 and contains all activities
    """
    # Arrange
    # (client fixture from conftest)
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4  # We have 4 test activities


def test_get_activities_contains_required_fields(client):
    """Test that each activity has all required fields.
    
    AAA Pattern:
    - Arrange: TestClient is ready
    - Act: Make GET request to /activities
    - Assert: Each activity has description, schedule, max_participants, participants
    """
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name, activity_info in data.items():
        assert set(activity_info.keys()) == required_fields
        assert isinstance(activity_info["participants"], list)
        assert isinstance(activity_info["max_participants"], int)
        assert isinstance(activity_info["description"], str)
        assert isinstance(activity_info["schedule"], str)


def test_get_activities_returns_participants_list(client):
    """Test that activities with participants show them correctly.
    
    AAA Pattern:
    - Arrange: Know which activities have participants from test data
    - Act: Request activities
    - Assert: Participants list matches expected data
    """
    # Arrange
    expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
    expected_gym_participants = []
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert data["Chess Club"]["participants"] == expected_chess_participants
    assert data["Gym Class"]["participants"] == expected_gym_participants


def test_get_activities_availability_calculation(client):
    """Test that availability is correctly calculated as max - current participants.
    
    AAA Pattern:
    - Arrange: Know test data (max and current participants)
    - Act: Request activities
    - Assert: Can calculate spots left (max_participants - len(participants))
    """
    # Arrange
    # Chess Club: max 12, has 2 participants = 10 spots left
    # Gym Class: max 30, has 0 participants = 30 spots left
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert - verify the api returns correct data for calculation
    assert data["Chess Club"]["max_participants"] == 12
    assert len(data["Chess Club"]["participants"]) == 2
    
    assert data["Gym Class"]["max_participants"] == 30
    assert len(data["Gym Class"]["participants"]) == 0
