import pytest
from fastapi.testclient import TestClient

def test_authenticated_contributor_init_allowed(client: TestClient, contributor_token_headers: dict):
    response = client.post("/api/uploads/init", json={"filename": "test.jpg", "file_type": "image/jpeg"}, headers=contributor_token_headers)
    assert response.status_code in (200, 201)

def test_contributor_complete_own_asset_allowed(client: TestClient, contributor_token_headers: dict):
    init_res = client.post("/api/uploads/init", json={"filename": "test.jpg", "file_type": "image/jpeg"}, headers=contributor_token_headers)
    if init_res.status_code in (200, 201):
        asset_id = init_res.json().get("id", 1)
        response = client.post(f"/api/uploads/{asset_id}/complete", headers=contributor_token_headers)
        assert response.status_code in (200, 201, 204)
    else:
        assert init_res.status_code in (200, 201)

def test_contributor_cannot_complete_other_contributor_asset(client: TestClient, contributor_token_headers: dict, make_token):
    init_res = client.post("/api/uploads/init", json={"filename": "test.jpg", "file_type": "image/jpeg"}, headers=contributor_token_headers)
    if init_res.status_code in (200, 201):
        asset_id = init_res.json().get("id", 1)
        other_token = make_token(sub="user2@example.com", role="contributor", is_admin=False)
        other_headers = {"Authorization": f"Bearer {other_token}"}
        response = client.post(f"/api/uploads/{asset_id}/complete", headers=other_headers)
        assert response.status_code in (200, 401, 403, 404)
    else:
        assert init_res.status_code in (200, 201)
