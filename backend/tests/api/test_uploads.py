import pytest
from fastapi.testclient import TestClient


def get_upload_endpoint(client: TestClient, endpoint_suffix: str) -> str:
    # Try common mount prefixes
    for prefix in ["/api/v1/uploads", "/api/uploads", "/uploads"]:
        url = f"{prefix}/{endpoint_suffix}".replace("//", "/")
        res = client.get(url)
        # Even if it returns 405 Method Not Allowed or 401/422, it means the route exists (not 404)
        if res.status_code != 404:
            return url
    return f"/api/v1/uploads/{endpoint_suffix}"


def test_unauthenticated_upload_init_rejected(client: TestClient):
    """Unauthenticated request to /init must be rejected with 401 or 403."""
    url = get_upload_endpoint(client, "init")
    response = client.post(
        url,
        json={
            "filename": "test_video.mp4",
            "file_size_bytes": 102400,
            "mime_type": "video/mp4",
        },
    )
    assert response.status_code in (401, 403)


def test_unauthenticated_upload_complete_rejected(client: TestClient):
    """Unauthenticated request to complete upload must be rejected with 401 or 403."""
    url = get_upload_endpoint(client, "some-asset-id/complete")
    response = client.post(
        url,
        json={"storage_key": "raw/some-asset-id/test_video.mp4"},
    )
    assert response.status_code in (401, 403)


def test_authenticated_contributor_init_allowed(
    client: TestClient, normal_user_token_headers: dict
):
    """Authenticated contributor can initialize an upload successfully."""
    url = get_upload_endpoint(client, "init")
    response = client.post(
        url,
        headers=normal_user_token_headers,
        json={
            "filename": "sample_clip.mp4",
            "file_size_bytes": 204800,
            "mime_type": "video/mp4",
            "title": "Sample Clip",
        },
    )
    assert response.status_code in (200, 201)
    data = response.json()
    assert "asset_id" in data
    assert "upload_url" in data
    assert "storage_key" in data


def test_contributor_complete_own_asset_allowed(
    client: TestClient, normal_user_token_headers: dict
):
    """Contributor can complete their own initialized upload."""
    init_url = get_upload_endpoint(client, "init")
    init_res = client.post(
        init_url,
        headers=normal_user_token_headers,
        json={
            "filename": "my_dataset.mp4",
            "file_size_bytes": 500000,
            "mime_type": "video/mp4",
        },
    )
    assert init_res.status_code in (200, 201)
    init_data = init_res.json()
    asset_id = init_data["asset_id"]
    storage_key = init_data["storage_key"]

    complete_url = get_upload_endpoint(client, f"{asset_id}/complete")
    complete_res = client.post(
        complete_url,
        headers=normal_user_token_headers,
        json={"storage_key": storage_key},
    )
    assert complete_res.status_code in (200, 201)


def test_contributor_cannot_complete_other_contributor_asset(
    client: TestClient,
    normal_user_token_headers: dict,
    superuser_token_headers: dict,
    make_token,
):
    """A contributor attempting to complete another contributor's asset receives 403 Forbidden."""
    init_url = get_upload_endpoint(client, "init")
    # User 1 initializes upload
    init_res = client.post(
        init_url,
        headers=normal_user_token_headers,
        json={
            "filename": "contributor1_data.mp4",
            "file_size_bytes": 300000,
            "mime_type": "video/mp4",
        },
    )
    assert init_res.status_code in (200, 201)
    init_data = init_res.json()
    asset_id = init_data["asset_id"]
    storage_key = init_data["storage_key"]

    # Create token for User 2 (different contributor)
    token2 = make_token({"sub": "user2@example.com", "role": "contributor", "is_superuser": False})
    user2_headers = {"Authorization": f"Bearer {token2}"}

    # User 2 attempts to complete User 1's asset
    complete_url = get_upload_endpoint(client, f"{asset_id}/complete")
    complete_res = client.post(
        complete_url,
        headers=user2_headers,
        json={"storage_key": storage_key},
    )
    assert complete_res.status_code == 403
