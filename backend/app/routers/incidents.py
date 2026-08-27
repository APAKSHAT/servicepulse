from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Incident
from app.schemas import IncidentRead

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    status: str = Query(default="all", regex="^(all|open|resolved)$"),
    db: AsyncSession = Depends(get_db),
):
    """List incidents, optionally filtered by open or resolved status."""
    stmt = select(Incident).order_by(Incident.started_at.desc())

    if status == "open":
        stmt = stmt.where(Incident.resolved_at.is_(None))
    elif status == "resolved":
        stmt = stmt.where(Incident.resolved_at.isnot(None))

    result = await db.execute(stmt)
    incidents = result.scalars().all()

    items: list[IncidentRead] = []
    for inc in incidents:
        # Eager-load the endpoint relationship for name/url.
        await db.refresh(inc, ["endpoint"])
        items.append(
            IncidentRead(
                id=inc.id,
                endpoint_id=inc.endpoint_id,
                endpoint_name=inc.endpoint.name if inc.endpoint else None,
                endpoint_url=inc.endpoint.url if inc.endpoint else None,
                started_at=inc.started_at,
                resolved_at=inc.resolved_at,
                failure_count=inc.failure_count,
            )
        )
    return items
