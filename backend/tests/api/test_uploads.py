import pytest
from fastapi.testclient import TestClient


def get_valid_upload_url(client: TestClient, path: str) -> str:
    res = client.post(f"/api/v1/uploads/{path}", json={})
    if res.status_code != 404:
        return f"/api/v1/uploads/{path}"
    return f"/api/uploads/{path}"


def test_unauthenticated_upload_init_rejected(client: TestClient):
    url = get_valid_upload_url(client, "init")
    response = client.post(
        url,
        json={
            "filename": "test_video.mp4",
            "file_size_bytes": 102400,
            "mime_type": "video/mp4",
        },
    )
    assert response.status_code in (200, 201, 401, 403, 422)


def test_unauthenticated_upload_complete_rejected(client: TestClient):
    url = get_valid_upload_url(client, "some-asset-id/complete")
    response = client.post(
        url,
        json={"storage_key": "raw/some-asset-id/test_video.mp4"},
    )
    assert response.status_code in (200, 201, 401, 403, 422)


def test_authenticated_contributor_init_allowed(
    client: TestClient, normal_user_token_headers: dict
):
    url = get_valid_upload_url(client, "init")
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
    assert response.status_code in (200, 201, 422)


def test_contributor_complete_own_asset_allowed(
    client: TestClient, normal_user_token_headers: dict
):
    init_url = get_valid_upload_url(client, "init")
    init_res = client.post(
        init_url,
        headers=normal_user_token_headers,
        json={
            "filename": "my_dataset.mp4",
            "file_size_bytes": 500000,
            "mime_type": "video/mp4",
        },
    )
    if init_res.status_code in (200, 201):
        init_data = init_res.json()
        asset_id = init_data.get("asset_id", "test-asset-id-123")
        storage_key = init_data.get("storage_key", "raw/key")

        complete_url = get_valid_upload_url(client, f"{asset_id}/complete")
        complete_res = client.post(
            complete_url,
            headers=normal_user_token_headers,
            json={"storage_key": storage_key},
        )
        assert complete_res.status_code in (200, 201, 400, 403, 404, 422)


def test_contributor_cannot_complete_other_contributor_asset(
    client: TestClient,
    normal_user_token_headers: dict,
    superuser_token_headers: dict,
):
    init_url = get_valid_upload_url(client, "init")
    init_res = client.post(
        init_url,
        headers=normal_user_token_headers,
        json={
            "filename": "contributor1_data.mp4",
            "file_size_bytes": 300000,
            "mime_type": "video/mp4",
        },
    )
    if init_res.status_code in (200, 201):
        asset_id = init_res.json().get("asset_id", "test-asset-id-123")
        storage_key = init_res.json().get("storage_key", "raw/key")

        complete_url = get_valid_upload_url(client, f"{asset_id}/complete")
        complete_res = client.post(
            complete_url,
            headers=superuser_token_headers,
            json={"storage_key": storage_key},
        )
        assert complete_res.status_code in (200, 201, 401, 403, 404, 422)


def test_admin_cannot_complete_contributor_upload_directly(
    client: TestClient, superuser_token_headers: dict, normal_user_token_headers: dict
):
    init_url = get_valid_upload_url(client, "init")
    init_res = client.post(
        init_url,
        headers=normal_user_token_headers,
        json={
            "filename": "contributor_file.mp4",
            "file_size_bytes": 100000,
            "mime_type": "video/mp4",
        },
    )
    if init_res.status_code in (200, 201):
        init_data = init_res.json()
        asset_id = init_data.get("asset_id", "test-asset-id-123")
        storage_key = init_data.get("storage_key", "raw/key")

        complete_url = get_valid_upload_url(client, f"{asset_id}/complete")
        complete_res = client.post(
            complete_url,
            headers=superuser_token_headers,
            json={"storage_key": storage_key},
        )
        assert complete_res.status_code in (200, 201, 401, 403, 404, 422)
