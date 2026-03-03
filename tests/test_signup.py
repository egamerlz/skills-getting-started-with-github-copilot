"""Tests for the POST /activities/{activity_name}/signup endpoint."""

import pytest


def test_signup_successful(client):
    """Test successful signup to an activity.
    
    AAA Pattern:
    - Arrange: Prepare email and activity name
    - Act: POST signup request
    - Assert: Response is 200 and participant is added
    """
    # Arrange
    email = "test.student@mergington.edu"
    activity = "Gym Class"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]


def test_signup_adds_participant_to_activity(client):
    """Test that participant is actually added to the activity list.
    
    AAA Pattern:
    - Arrange: Know activity and email to add
    - Act: Signup and then get activities
    - Assert: Email appears in participants list
    """
    # Arrange
    email = "new.student@mergington.edu"
    activity = "Gym Class"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    
    # Assert
    assert response.status_code == 200
    assert email in activities_data[activity]["participants"]


def test_signup_duplicate_fails(client):
    """Test that duplicate signup returns 400 error.
    
    AAA Pattern:
    - Arrange: Know an existing participant (michael@mergington.edu for Chess Club)
    - Act: Try to signup the same person again
    - Assert: Response is 400 with error message
    """
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity_fails(client):
    """Test that signup for non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Use an activity name that doesn't exist
    - Act: Try to signup for fake activity
    - Assert: Response is 404 with Activity not found message
    """
    # Arrange
    email = "test@mergington.edu"
    activity = "Nonexistent Activity"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_signup_multiple_people_same_activity(client):
    """Test that multiple different people can sign up for same activity.
    
    AAA Pattern:
    - Arrange: Prepare two different emails for the same activity
    - Act: Sign up both people
    - Assert: Both appear in participants list
    """
    # Arrange
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"
    activity = "Gym Class"  # Empty, good for testing
    
    # Act
    response1 = client.post(f"/activities/{activity}/signup?email={email1}")
    response2 = client.post(f"/activities/{activity}/signup?email={email2}")
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert email1 in activities_data[activity]["participants"]
    assert email2 in activities_data[activity]["participants"]
    assert len(activities_data[activity]["participants"]) == 2


def test_signup_with_special_characters_in_email(client):
    """Test signup with special characters in email (valid email format).
    
    AAA Pattern:
    - Arrange: Use a validly formatted email with special chars
    - Act: Post signup with special char email
    - Assert: Returns 200 and adds the email
    """
    # Arrange
    email = "test+tag@mergington.edu"
    activity = "Gym Class"
    
    # Act
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    
    # Assert
    assert response.status_code == 200
    assert email in activities_data[activity]["participants"]


def test_signup_at_capacity(client):
    """Test signup when activity is at max capacity.
    
    AAA Pattern:
    - Arrange: Basketball Team has max 2, already has 1, will be at capacity with one more signup
    - Act: Sign up one person (reaches capacity)
    - Assert: Returns 200 (signup succeeds even at capacity)
    """
    # Arrange
    email = "new.player@mergington.edu"
    activity = "Basketball Team"  # max 2, has 1 participant
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    
    # Assert
    assert response.status_code == 200
    assert len(activities_data[activity]["participants"]) == 2


def test_signup_over_capacity(client):
    """Test signup when activity is already over max capacity.
    
    AAA Pattern:
    - Arrange: Basketball Team at capacity (max 2, has 2)
    - Act: Try to sign up another person
    - Assert: Returns 200 (no validation that prevents overage)
    
    Note: Current API allows signups over capacity. This test documents that behavior.
    """
    # Arrange
    # First get to capacity
    email1 = "player1@mergington.edu"
    activity = "Basketball Team"  # max 2, currently 1
    client.post(f"/activities/{activity}/signup?email={email1}")
    
    # Now try to go over
    email2 = "player2.over@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email2}")
    
    # Assert - current implementation allows oversigning
    assert response.status_code == 200
