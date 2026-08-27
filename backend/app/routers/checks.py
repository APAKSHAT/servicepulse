import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Check, Endpoint
from app.schemas import CheckRead, DashboardSummary

router = APIRouter(prefix="/api", tags=["checks"])


@router.get("/endpoints/{endpoint_id}/checks", response_model=list[CheckRead])
async def list_checks(
    endpoint_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Return check history for one endpoint within the given time window."""
    endpoint = await db.get(Endpoint, endpoint_id)
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")

    since = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=hours)
    stmt = (
        select(Check)
        .where(Check.endpoint_id == endpoint_id, Check.checked_at >= since)
        .order_by(Check.checked_at.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary(db: AsyncSession = Depends(get_db)):
    """Aggregate stats for the dashboard header."""
    total = await db.scalar(select(func.count(Endpoint.id)))
    active = await db.scalar(
        select(func.count(Endpoint.id)).where(Endpoint.is_active.is_(True))
    )

    # Count open incidents (resolved_at IS NULL).
    from app.models import Incident

    open_incidents = await db.scalar(
        select(func.count(Incident.id)).where(Incident.resolved_at.is_(None))
    )

    # Compute overall uptime % from checks in the last 24 hours.
    since = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
    total_checks = await db.scalar(
        select(func.count(Check.id)).where(Check.checked_at >= since)
    )
    successful_checks = await db.scalar(
        select(func.count(Check.id)).where(
            Check.checked_at >= since,
            Check.status_code.isnot(None),
            Check.status_code < 400,
        )
    )

    uptime_pct = 0.0
    if total_checks and total_checks > 0:
        uptime_pct = round((successful_checks / total_checks) * 100, 2)

    return DashboardSummary(
        total_endpoints=total or 0,
        active_endpoints=active or 0,
        active_incidents=open_incidents or 0,
        overall_uptime_pct=uptime_pct,
    )
