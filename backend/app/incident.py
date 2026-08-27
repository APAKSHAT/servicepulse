import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Incident


async def process_check(
    db: AsyncSession,
    endpoint_id: int,
    is_success: bool,
) -> Incident | None:
    """Handle incident lifecycle after a check completes.

    Groups consecutive failures into a single open incident rather than
    creating a new incident for every failing check. When the endpoint
    recovers, the open incident is resolved.

    Returns the affected incident (created, updated, or resolved), or
    ``None`` when a successful check has no open incident to close.
    """
    open_incident = await _get_open_incident(db, endpoint_id)

    if not is_success:
        if open_incident is None:
            incident = Incident(endpoint_id=endpoint_id, failure_count=1)
            db.add(incident)
        else:
            open_incident.failure_count += 1
            incident = open_incident
        await db.commit()
        await db.refresh(incident)
        return incident

    # Successful check — resolve any open incident.
    if open_incident is not None:
        open_incident.resolved_at = datetime.datetime.now(datetime.UTC)
        await db.commit()
        await db.refresh(open_incident)
        return open_incident

    return None


async def _get_open_incident(
    db: AsyncSession,
    endpoint_id: int,
) -> Incident | None:
    """Return the open (unresolved) incident for an endpoint, if any."""
    stmt = (
        select(Incident)
        .where(Incident.endpoint_id == endpoint_id, Incident.resolved_at.is_(None))
        .order_by(Incident.started_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
