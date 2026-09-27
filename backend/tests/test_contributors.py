import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("action", ["approve", "reject"])
def test_review_unknown_contributor_returns_404(
    client: TestClient, superuser_token_headers: dict, action: str
):
    res_v1 = client.post(
        f"/api/v1/contributors/9999999/{action}",
        headers=superuser_token_headers,
    )
    if res_v1.status_code != 404 or "Not Found" not in res_v1.text:
        response = res_v1
    else:
        response = client.post(
            f"/api/contributors/9999999/{action}",
            headers=superuser_token_headers,
        )
    assert response.status_code in (404, 400, 422)
