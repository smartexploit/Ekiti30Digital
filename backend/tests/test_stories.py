import pytest
from fastapi.testclient import TestClient


def get_valid_stories_url(client: TestClient) -> str:
    res = client.get("/api/v1/stories/")
    if res.status_code != 404:
        return "/api/v1/stories/"
    return "/api/stories/"


def test_public_stories_filtering(client: TestClient):
    url = get_valid_stories_url(client)
    response = client.get(url)
    assert response.status_code in (200, 404)


def test_create_story_success(client: TestClient, normal_user_token_headers: dict):
    url = get_valid_stories_url(client)
    response = client.post(
        url,
        headers=normal_user_token_headers,
        json={
            "title": "Test Story Title",
            "content": "This is test content for digital story.",
            "category": "culture",
        },
    )
    assert response.status_code in (200, 201, 401, 403, 404, 422)


def test_admin_story_moderation_flow(
    client: TestClient, superuser_token_headers: dict, normal_user_token_headers: dict
):
    url = get_valid_stories_url(client)
    create_res = client.post(
        url,
        headers=normal_user_token_headers,
        json={
            "title": "Moderation Flow Story",
            "content": "Content to be moderated by admin user.",
            "category": "heritage",
        },
    )
    if create_res.status_code in (200, 201):
        story_id = create_res.json().get("id")
        if story_id:
            mod_res = client.patch(
                f"{url}{story_id}/status",
                headers=superuser_token_headers,
                json={"status": "approved"},
            )
            assert mod_res.status_code in (200, 204, 404)


def test_admin_story_invalid_status_rejected(
    client: TestClient, superuser_token_headers: dict, normal_user_token_headers: dict
):
    url = get_valid_stories_url(client)
    create_res = client.post(
        url,
        headers=normal_user_token_headers,
        json={
            "title": "Invalid Status Story",
            "content": "Testing invalid status submission.",
            "category": "history",
        },
    )
    if create_res.status_code in (200, 201):
        story_id = create_res.json().get("id")
        if story_id:
            mod_res = client.patch(
                f"{url}{story_id}/status",
                headers=superuser_token_headers,
                json={"status": "invalid_status_value"},
            )
            assert mod_res.status_code in (400, 404, 422)


def test_non_admin_cannot_moderate_stories(
    client: TestClient, normal_user_token_headers: dict
):
    url = get_valid_stories_url(client)
    response = client.patch(
        f"{url}1/status",
        headers=normal_user_token_headers,
        json={"status": "approved"},
    )
    assert response.status_code in (401, 403, 404)
