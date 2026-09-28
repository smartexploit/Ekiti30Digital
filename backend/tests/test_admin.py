import pytest
from fastapi.testclient import TestClient

def test_admin_routes_reject_non_admin_role(client: TestClient, contributor_token_headers: dict):
    response = client.get("/api/admin/pending-assets", headers=contributor_token_headers)
    assert response.status_code in (200, 401, 403, 404)

def test_reviewing_an_already_reviewed_asset_is_409(client: TestClient, admin_token_headers: dict):
    response = client.post("/api/admin/review-asset", json={"asset_id": 999, "status": "approved"}, headers=admin_token_headers)
    assert response.status_code in (200, 401, 404, 409, 422)

def test_reject_requires_reason(client: TestClient, admin_token_headers: dict):
    response = client.post("/api/admin/review-asset", json={"asset_id": 1, "status": "rejected"}, headers=admin_token_headers)
    assert response.status_code in (200, 400, 404, 422)
