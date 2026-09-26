import pytest
from app.models.story import Story

def test_create_story_success(client):
    response = client.post("/api/stories", json={
        "title": "My Ekiti Story",
        "content": "This is a wonderful story about Ekiti development.",
        "author": "Oluwaseun"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Ekiti Story"
    assert data["status"] == "pending"
    assert "id" in data

def test_create_story_validation_failure(client):
    response = client.post("/api/stories", json={
        "title": "",
        "content": ""
    })
    assert response.status_code == 422

def test_public_stories_filtering(client, db_session):
    approved_story = Story(title="Approved Story", content="Approved content", status="approved")
    pending_story = Story(title="Pending Story", content="Pending content", status="pending")
    rejected_story = Story(title="Rejected Story", content="Rejected content", status="rejected")
    
    db_session.add_all([approved_story, pending_story, rejected_story])
    db_session.commit()

    response = client.get("/api/stories")
    assert response.status_code == 200
    stories = response.json()
    
    # Strict public filtering check: only approved stories should be returned
    assert len(stories) == 1
    assert stories[0]["title"] == "Approved Story"
    assert stories[0]["status"] == "approved"
