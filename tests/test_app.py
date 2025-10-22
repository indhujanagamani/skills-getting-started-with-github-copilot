import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert response.json() == activities

def test_signup_for_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # Make sure the email is not already registered
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]

def test_signup_for_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_duplicate():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using an email we know is already registered
    
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}

def test_unregister_from_activity():
    activity_name = "Chess Club"
    email = "test_unregister@mergington.edu"
    
    # First, register the student
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)
    
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]

def test_unregister_from_nonexistent_activity():
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "not_registered@mergington.edu"
    
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not registered for this activity"}