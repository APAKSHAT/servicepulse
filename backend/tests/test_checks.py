import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Check, Endpoint


@pytest.mark.asyncio
async def test_list_checks_empty(client: AsyncClient):
    """Checks endpoint returns empty list for a new endpoint."""
    create_resp = await client.post(
        "/api/endpoints",
        json={"url": "https://example.com", "name": "Test"},
    )
    endpoint_id = create_resp.json()["id"]

    resp = await client.get(f"/api/endpoints/{endpoint_id}/checks")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_checks_with_data(client: AsyncClient, db_session: AsyncSession):
    """Checks appear after being recorded."""
    ep = Endpoint(url="https://example.com", name="Test", interval_seconds=30)
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)

    for status in [200, 200, 500]:
        check = Check(endpoint_id=ep.id, status_code=status, response_time_ms=50.0)
        db_session.add(check)
    await db_session.commit()

    resp = await client.get(f"/api/endpoints/{ep.id}/checks")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[2]["status_code"] == 500


@pytest.mark.asyncio
async def test_dashboard_summary(client: AsyncClient):
    resp = await client.get("/api/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_endpoints" in data
    assert "overall_uptime_pct" in data
