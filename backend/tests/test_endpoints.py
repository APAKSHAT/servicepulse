import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_endpoint(client: AsyncClient):
    resp = await client.post(
        "/api/endpoints",
        json={"url": "https://example.com", "name": "Example", "interval_seconds": 60},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Example"
    assert data["url"] == "https://example.com/"
    assert data["interval_seconds"] == 60
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_list_endpoints(client: AsyncClient):
    await client.post(
        "/api/endpoints",
        json={"url": "https://example.com", "name": "First"},
    )
    await client.post(
        "/api/endpoints",
        json={"url": "https://second.com", "name": "Second"},
    )

    resp = await client.get("/api/endpoints")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_endpoint_detail(client: AsyncClient):
    create_resp = await client.post(
        "/api/endpoints",
        json={"url": "https://httpbin.org/get", "name": "HTTPBin"},
    )
    endpoint_id = create_resp.json()["id"]

    resp = await client.get(f"/api/endpoints/{endpoint_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "HTTPBin"


@pytest.mark.asyncio
async def test_get_endpoint_not_found(client: AsyncClient):
    resp = await client.get("/api/endpoints/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_endpoint(client: AsyncClient):
    create_resp = await client.post(
        "/api/endpoints",
        json={"url": "https://example.com", "name": "ToDelete"},
    )
    endpoint_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/endpoints/{endpoint_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/endpoints/{endpoint_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_endpoint(client: AsyncClient):
    create_resp = await client.post(
        "/api/endpoints",
        json={"url": "https://example.com", "name": "Original"},
    )
    endpoint_id = create_resp.json()["id"]

    resp = await client.patch(
        f"/api/endpoints/{endpoint_id}",
        json={"name": "Renamed", "is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"
    assert resp.json()["is_active"] is False
