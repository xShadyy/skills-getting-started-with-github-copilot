import copy
from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_activities():
    """Backup and restore the in-memory activities dict for each test."""
    backup = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(backup)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_creates_participant_and_prevents_duplicate():
    activity = "Art Studio"
    email = "test.user@example.com"

    # ensure not present initially
    resp = client.get("/activities")
    assert resp.status_code == 200

    # signup first time
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200
    assert "Signed up" in r1.json().get("message", "")

    # signup second time should be rejected (duplicate)
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400
    assert r2.json().get("detail") == "Student already registered for this activity"


def test_signup_enforces_capacity():
    activity = "Soccer Team"
    # set small capacity for test
    activities[activity]["max_participants"] = 1
    # ensure participants empty
    activities[activity]["participants"] = []

    r1 = client.post(f"/activities/{activity}/signup?email=a@example.com")
    assert r1.status_code == 200

    r2 = client.post(f"/activities/{activity}/signup?email=b@example.com")
    assert r2.status_code == 400
    assert r2.json().get("detail") == "Activity is full"


def test_unregister_removes_participant():
    activity = "Debate Team"
    email = "remove.me@example.com"

    # ensure participant registered
    r1 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r1.status_code == 200

    # unregister
    r2 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 200
    assert "Unregistered" in r2.json().get("message", "")

    # unregistering again should return 404
    r3 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert r3.status_code == 404
    assert r3.json().get("detail") == "Student not registered for this activity"
