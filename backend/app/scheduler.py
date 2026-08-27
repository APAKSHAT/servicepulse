import logging

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.incident import process_check
from app.models import Check, Endpoint

logger = logging.getLogger("servicepulse.scheduler")

scheduler = AsyncIOScheduler()


async def poll_endpoint(endpoint_id: int, url: str) -> None:
    """Send a GET request to *url* and record the result."""
    status_code: int | None = None
    response_time_ms: float | None = None
    error: str | None = None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            status_code = resp.status_code
            response_time_ms = resp.elapsed.total_seconds() * 1000
    except httpx.TimeoutException:
        error = "Request timed out"
        logger.warning("Timeout polling %s", url)
    except httpx.RequestError as exc:
        error = str(exc)
        logger.warning("Error polling %s: %s", url, exc)

    async with async_session() as db:
        check = Check(
            endpoint_id=endpoint_id,
            status_code=status_code,
            response_time_ms=response_time_ms,
            error=error,
        )
        db.add(check)
        await db.commit()

        is_success = status_code is not None and status_code < 400
        await process_check(db, endpoint_id, is_success)

    logger.info(
        "Polled %s — status=%s time=%.1fms",
        url,
        status_code,
        response_time_ms or 0,
    )


async def sync_jobs(db: AsyncSession) -> None:
    """Rebuild the scheduler's job list from the database.

    Called at startup and whenever endpoints are added or removed so
    that the polling schedule stays in sync with the database.
    """
    # Remove all existing poll jobs.
    for job in scheduler.get_jobs():
        if job.id.startswith("poll_"):
            job.remove()

    result = await db.execute(
        select(Endpoint).where(Endpoint.is_active.is_(True))
    )
    endpoints = result.scalars().all()

    for ep in endpoints:
        scheduler.add_job(
            poll_endpoint,
            "interval",
            seconds=ep.interval_seconds,
            id=f"poll_{ep.id}",
            args=[ep.id, ep.url],
            replace_existing=True,
        )

    logger.info("Synced %d polling jobs", len(endpoints))
