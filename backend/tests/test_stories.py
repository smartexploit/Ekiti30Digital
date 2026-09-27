from fastapi.testclient import TestClient
from fastapi import status

def test_public_stories_filtering(client: TestClient):
    """Public endpoint returns only approved stories, excluding pending/rejected."""
    response = client.get("/api/stories")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Ensure response format is correct (list or paginated object)
    stories = data if isinstance(data, list) else data.get("items", [])
    for story in stories:
        assert story.get("status") == "approved"

def test_create_story_success(client: TestClient, normal_user_token_headers: dict):
    """Valid story submission returns 201 Created and sets status to pending."""
    response = client.post(
        "/api/stories",
        headers=normal_user_token_headers,
        json={
            "title": "My Ekiti Heritage",
            "content": "A story about cultural roots in Ekiti State.",
            "category": "culture"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data.get("status") == "pending"
    assert "id" in data or "story_id" in data

def test_create_story_invalid_payload(client: TestClient, normal_user_token_headers: dict):
    """Invalid payload returns 422 Unprocessable Entity."""
    response = client.post(
        "/api/stories",
        headers=normal_user_token_headers,
        json={
            "title": "", # Invalid empty title
            "content": ""
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_admin_story_moderation_flow(client: TestClient, normal_user_token_headers: dict, superuser_token_headers: dict):
    """Full story submission and admin moderation flow (approve/reject)."""
    # 1. Contributor creates story
    create_res = client.post(
        "/api/stories",
        headers=normal_user_token_headers,
        json={
            "title": "Fountain of Knowledge",
            "content": "Reflections on education in Ekiti.",
            "category": "education"
        }
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    story_data = create_res.json()
    story_id = story_data.get("id") or story_data.get("story_id")

    # 2. Admin moderates story via correct admin endpoint
    mod_url = f"/api/admin/stories/{story_id}/status"
    mod_res = client.patch(
        mod_url,
        headers=superuser_token_headers,
        json={"status": "approved", "review_notes": "Looks good"}
    )
    assert mod_res.status_code == status.HTTP_200_OK
    assert mod_res.json().get("status") == "approved"

def test_admin_story_invalid_status_rejected(client: TestClient, normal_user_token_headers: dict, superuser_token_headers: dict):
    """Admin moderation with invalid status value returns 422."""
    create_res = client.post(
        "/api/stories",
        headers=normal_user_token_headers,
        json={
            "title": "Test Story",
            "content": "Test content for invalid status.",
        }
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    story_id = create_res.json().get("id") or create_res.json().get("story_id")

    mod_url = f"/api/admin/stories/{story_id}/status"
    mod_res = client.patch(
        mod_url,
        headers=superuser_token_headers,
        json={"status": "invalid_status_value"}
    )
    assert mod_res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_non_admin_cannot_moderate_stories(client: TestClient, normal_user_token_headers: dict):
    """Non-admin contributors receive 403 Forbidden when attempting moderation."""
    mod_url = "/api/admin/stories/some_story_id/status"
    mod_res = client.patch(
        mod_url,
        headers=normal_user_token_headers,
        json={"status": "approved"}
    )
    assert mod_res.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
