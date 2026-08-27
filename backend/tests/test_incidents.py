import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.incident import process_check
from app.models import Endpoint, Incident


@pytest.mark.asyncio
async def test_failure_creates_incident(db_session: AsyncSession):
    """First failure on an endpoint creates a new incident."""
    ep = Endpoint(url="https://example.com", name="Test")
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)

    incident = await process_check(db_session, ep.id, is_success=False)
    assert incident is not None
    assert incident.failure_count == 1
    assert incident.resolved_at is None


@pytest.mark.asyncio
async def test_repeated_failures_same_incident(db_session: AsyncSession):
    """Consecutive failures increment the existing incident instead of creating new ones."""
    ep = Endpoint(url="https://example.com", name="Test")
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)

    inc1 = await process_check(db_session, ep.id, is_success=False)
    inc2 = await process_check(db_session, ep.id, is_success=False)
    inc3 = await process_check(db_session, ep.id, is_success=False)

    assert inc1.id == inc2.id == inc3.id
    assert inc3.failure_count == 3


@pytest.mark.asyncio
async def test_success_resolves_incident(db_session: AsyncSession):
    """A successful check resolves the open incident."""
    ep = Endpoint(url="https://example.com", name="Test")
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)

    await process_check(db_session, ep.id, is_success=False)
    await process_check(db_session, ep.id, is_success=False)
    resolved = await process_check(db_session, ep.id, is_success=True)

    assert resolved is not None
    assert resolved.resolved_at is not None
    assert resolved.failure_count == 2


@pytest.mark.asyncio
async def test_success_without_incident(db_session: AsyncSession):
    """A successful check with no open incident returns None."""
    ep = Endpoint(url="https://example.com", name="Test")
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)

    result = await process_check(db_session, ep.id, is_success=True)
    assert result is None


@pytest.mark.asyncio
async def test_new_incident_after_recovery(db_session: AsyncSession):
    """After recovery, a new failure creates a second incident."""
    ep = Endpoint(url="https://example.com", name="Test")
    db_session.add(ep)
    await db_session.commit()
    await db_session.refresh(ep)

    first = await process_check(db_session, ep.id, is_success=False)
    await process_check(db_session, ep.id, is_success=True)
    second = await process_check(db_session, ep.id, is_success=False)

    assert first.id != second.id
    assert second.failure_count == 1
