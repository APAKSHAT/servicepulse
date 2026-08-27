from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Check, Endpoint
from app.schemas import EndpointCreate, EndpointRead, EndpointUpdate
from app.scheduler import sync_jobs

router = APIRouter(prefix="/api/endpoints", tags=["endpoints"])


@router.get("", response_model=list[EndpointRead])
async def list_endpoints(db: AsyncSession = Depends(get_db)):
    """Return every registered endpoint with its latest check status."""
    result = await db.execute(select(Endpoint).order_by(Endpoint.created_at.desc()))
    endpoints = result.scalars().all()

    items: list[EndpointRead] = []
    for ep in endpoints:
        latest = await _latest_check(db, ep.id)
        items.append(
            EndpointRead(
                id=ep.id,
                url=ep.url,
                name=ep.name,
                interval_seconds=ep.interval_seconds,
                is_active=ep.is_active,
                created_at=ep.created_at,
                latest_status=latest.status_code if latest else None,
                latest_response_time_ms=latest.response_time_ms if latest else None,
            )
        )
    return items


@router.post("", response_model=EndpointRead, status_code=201)
async def create_endpoint(
    payload: EndpointCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new URL to monitor."""
    endpoint = Endpoint(
        url=str(payload.url),
        name=payload.name,
        interval_seconds=payload.interval_seconds,
    )
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)

    await sync_jobs(db)

    return EndpointRead(
        id=endpoint.id,
        url=endpoint.url,
        name=endpoint.name,
        interval_seconds=endpoint.interval_seconds,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at,
    )


@router.get("/{endpoint_id}", response_model=EndpointRead)
async def get_endpoint(endpoint_id: int, db: AsyncSession = Depends(get_db)):
    endpoint = await db.get(Endpoint, endpoint_id)
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    latest = await _latest_check(db, endpoint.id)
    return EndpointRead(
        id=endpoint.id,
        url=endpoint.url,
        name=endpoint.name,
        interval_seconds=endpoint.interval_seconds,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at,
        latest_status=latest.status_code if latest else None,
        latest_response_time_ms=latest.response_time_ms if latest else None,
    )


@router.patch("/{endpoint_id}", response_model=EndpointRead)
async def update_endpoint(
    endpoint_id: int,
    payload: EndpointUpdate,
    db: AsyncSession = Depends(get_db),
):
    endpoint = await db.get(Endpoint, endpoint_id)
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "url" in update_data:
        update_data["url"] = str(update_data["url"])
    for key, value in update_data.items():
        setattr(endpoint, key, value)

    await db.commit()
    await db.refresh(endpoint)
    await sync_jobs(db)

    latest = await _latest_check(db, endpoint.id)
    return EndpointRead(
        id=endpoint.id,
        url=endpoint.url,
        name=endpoint.name,
        interval_seconds=endpoint.interval_seconds,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at,
        latest_status=latest.status_code if latest else None,
        latest_response_time_ms=latest.response_time_ms if latest else None,
    )


@router.delete("/{endpoint_id}", status_code=204)
async def delete_endpoint(endpoint_id: int, db: AsyncSession = Depends(get_db)):
    endpoint = await db.get(Endpoint, endpoint_id)
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    await db.delete(endpoint)
    await db.commit()
    await sync_jobs(db)


async def _latest_check(db: AsyncSession, endpoint_id: int) -> Check | None:
    """Return the most recent check for an endpoint."""
    stmt = (
        select(Check)
        .where(Check.endpoint_id == endpoint_id)
        .order_by(Check.checked_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
