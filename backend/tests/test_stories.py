import pytest
from app.models.story import Story

def test_create_story_success(client):
    response = client.post("/api/stories", json={
        "title": "My Ekiti Story",
        "content": "This is a wonderful story about Ekiti development.",
        "author": "Oluwaseun",
        "email": "oluwaseun@example.com",
        "category": "Culture"
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

def test_admin_story_moderation_flow(client, db_session, admin_headers):
    story = Story(title="Moderation Test", content="Content", status="pending")
    db_session.add(story)
    db_session.commit()

    # List pending stories as admin
    resp = client.get("/api/admin/stories/pending", headers=admin_headers)
    assert resp.status_code == 200
    assert any(s["id"] == story.id for s in resp.json())

    # Approve story
    resp = client.patch(f"/api/admin/stories/{story.id}/status", json={"status": "approved"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"

def test_admin_story_invalid_status_rejected(client, db_session, admin_headers):
    story = Story(title="Invalid Status Test", content="Content", status="pending")
    db_session.add(story)
    db_session.commit()

    # Send invalid status value
    resp = client.patch(f"/api/admin/stories/{story.id}/status", json={"status": "super_admin_status"}, headers=admin_headers)
    assert resp.status_code == 422

def test_non_admin_cannot_moderate_stories(client, db_session, make_token):
    story = Story(title="Security Test", content="Content", status="pending")
    db_session.add(story)
    db_session.commit()

    headers = {"Authorization": f"Bearer {make_token(role='member')}"}
    resp = client.patch(f"/api/admin/stories/{story.id}/status", json={"status": "approved"}, headers=headers)
    assert resp.status_code in (401, 403)
