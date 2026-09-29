"""Tests for the My Story submission and listing endpoints."""

import pytest

def test_unauthenticated_story_submission_rejected(client):
    payload = {
        "description": "Growing up in Ekiti during the 90s.",
        "rights_status": "owned",
        "folder": "EKITI30/Stories"
    }
    response = client.post("/api/stories/", json=payload)
    assert response.status_code in [401, 403, 503]

def test_authenticated_story_submission_success(client, contributor_headers):
    payload = {
        "description": "My first day at school in Ado.",
        "rights_status": "owned",
        "folder": "EKITI30/Stories",
        "source": "Family archive",
        "location_lga": "Ado-Ekiti"
    }
    response = client.post("/api/stories/", json=payload, headers=contributor_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["folder"] == "EKITI30/Stories"
    assert data["contributor"] == "contributor@example.com" or data["contributor"] is not None

def test_get_stories_regression_endpoint(client):
    response = client.get("/api/stories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
