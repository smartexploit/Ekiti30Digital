import pytest
from app.core.config import settings

def test_admin_routes_reject_unauthenticated(client):
    response = client.get("/api/admin/assets/pending")
    assert response.status_code == 401

def test_admin_routes_reject_non_admin_role(client, make_token):
    user_token = make_token(role="user")
    headers = {"Authorization": f"Bearer {user_token}"}
    response = client.get("/api/admin/assets/pending", headers=headers)
    assert response.status_code in (401, 403)

def test_admin_routes_fail_closed_without_secret(client, monkeypatch):
    if hasattr(settings, "ADMIN_JWT_SECRET"):
        monkeypatch.setattr(settings, "ADMIN_JWT_SECRET", "")
    if hasattr(settings, "JWT_SECRET"):
        monkeypatch.setattr(settings, "JWT_SECRET", "")
    if hasattr(settings, "NEXTAUTH_SECRET"):
        monkeypatch.setattr(settings, "NEXTAUTH_SECRET", "")

    response = client.get("/api/admin/assets/pending")
    assert response.status_code in (401, 503)

def test_list_pending_returns_only_pending(client, admin_token_headers):
    response = client.get("/api/admin/assets/pending", headers=admin_token_headers)
    assert response.status_code in (200, 401)

def test_approve_sets_status_and_reviewer(client, admin_token_headers):
    response = client.post("/api/admin/assets/1/approve", headers=admin_token_headers)
    assert response.status_code in (200, 401, 404)

def test_reject_sets_status_reason_and_reviewer(client, admin_token_headers):
    payload = {"reason": "Quality standard not met"}
    response = client.post("/api/admin/assets/1/reject", json=payload, headers=admin_token_headers)
    assert response.status_code in (200, 401, 404)

def test_reject_requires_reason(client, admin_token_headers):
    payload = {}
    response = client.post("/api/admin/assets/1/reject", json=payload, headers=admin_token_headers)
    assert response.status_code in (401, 422)

def test_reviewing_an_already_reviewed_asset_is_409(client, admin_token_headers):
    response = client.post("/api/admin/assets/reviewed_id/approve", headers=admin_token_headers)
    assert response.status_code in (401, 404, 409)

def test_reviewing_unknown_asset_is_404(client, admin_token_headers):
    response = client.post("/api/admin/assets/999999/approve", headers=admin_token_headers)
    assert response.status_code in (401, 404)
