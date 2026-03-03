"""Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

import pytest


def test_unregister_successful(client):
    """Test successful unregistration from an activity.
    
    AAA Pattern:
    - Arrange: Know an existing participant (daniel@mergington.edu in Chess Club)
    - Act: DELETE request to unregister
    - Assert: Response is 200 and participant count decreases
    """
    # Arrange
    email = "daniel@mergington.edu"
    activity = "Chess Club"
    
    # Get initial participant count
    activities_before = client.get("/activities").json()
    initial_count = len(activities_before[activity]["participants"])
    
    # Act
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    # Verify participant was removed
    activities_after = client.get("/activities").json()
    assert len(activities_after[activity]["participants"]) == initial_count - 1
    assert email not in activities_after[activity]["participants"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes participant from list.
    
    AAA Pattern:
    - Arrange: Know Chess Club has michael@mergington.edu
    - Act: Unregister michael
    - Assert: Participant no longer in list
    """
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    activities_after = client.get("/activities").json()
    
    # Assert
    assert response.status_code == 200
    assert email not in activities_after[activity]["participants"]


def test_unregister_nonexistent_participant_fails(client):
    """Test that unregistering non-existent participant returns 400.
    
    AAA Pattern:
    - Arrange: Use an email not in the activity
    - Act: Try to unregister non-existent participant
    - Assert: Response is 400 with error message
    """
    # Arrange
    email = "notarealstudent@mergington.edu"
    activity = "Chess Club"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_unregister_nonexistent_activity_fails(client):
    """Test that unregister from non-existent activity returns 404.
    
    AAA Pattern:
    - Arrange: Use a fake activity name
    - Act: Try to unregister from fake activity
    - Assert: Response is 404
    """
    # Arrange
    email = "test@mergington.edu"
    activity = "Fake Activity"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_twice_fails(client):
    """Test that unregistering same person twice fails second time.
    
    AAA Pattern:
    - Arrange: Know a participant to unregister twice
    - Act: Unregister once (success), then again (fail)
    - Assert: Second request returns 400
    """
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Act - first unregister
    response1 = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    # Try to unregister again
    response2 = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 400
    data = response2.json()
    assert "not registered" in data["detail"].lower()


def test_unregister_from_empty_activity(client):
    """Test unregister from activity with no participants.
    
    AAA Pattern:
    - Arrange: Use Gym Class which has no participants
    - Act: Try to unregister someone from empty activity
    - Assert: Returns 400 error
    """
    # Arrange
    email = "anyone@mergington.edu"
    activity = "Gym Class"  # Empty activity
    
    # Act
    response = client.delete(
        f"/activities/{activity}/unregister?email={email}"
    )
    
    # Assert
    assert response.status_code == 400


def test_unregister_one_from_many(client):
    """Test unregistering one participant when multiple exist.
    
    AAA Pattern:
    - Arrange: Programming Class has 1 participant (emma)
    - Act: Unregister emma
    - Assert: Emma is gone, but activity still exists
    """
    # Arrange
    email_to_remove = "emma@mergington.edu"
    activity = "Programming Class"
    
    # Act
    response = client.delete(
        f"/activities/{activity}/unregister?email={email_to_remove}"
    )
    activities_after = client.get("/activities").json()
    
    # Assert
    assert response.status_code == 200
    assert email_to_remove not in activities_after[activity]["participants"]
    # Activity should still have structure
    assert "description" in activities_after[activity]
    assert "max_participants" in activities_after[activity]


def test_unregister_with_special_characters(client):
    """Test unregister with special characters in email.
    
    AAA Pattern:
    - Arrange: First signup with special char email, then unregister
    - Act: Signup then unregister special char email
    - Assert: Both operations succeed
    """
    # Arrange
    email = "test+tag@mergington.edu"
    activity = "Gym Class"
    
    # Signup first
    client.post(f"/activities/{activity}/signup", params={"email": email})
    
    # Act - unregister
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    activities_after = client.get("/activities").json()
    
    # Assert
    assert response.status_code == 200
    assert email not in activities_after[activity]["participants"]
