import copy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


import pytest


@pytest.fixture(autouse=True)
def restore_activities():
    """Backup and restore the in-memory activities dict around each test."""
    backup = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(backup)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Ensure one of the known activities exists
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure student not already registered
    before = client.get("/activities").json()[activity]["participants"]
    assert email not in before

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify participant added
    after = client.get("/activities").json()[activity]["participants"]
    assert email in after

    # Attempt duplicate signup -> should return 400
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_un = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp_un.status_code == 200
    assert "Unregistered" in resp_un.json().get("message", "")

    # Ensure removed
    final = client.get("/activities").json()[activity]["participants"]
    assert email not in final


def test_unregister_nonexistent():
    activity = "Chess Club"
    email = "noone@nowhere.example"

    # should return 404 when participant not in activity
    resp = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 404
