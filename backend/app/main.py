import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import checks, endpoints, incidents
from app.scheduler import scheduler, sync_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)


from app.database import async_session

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: sync polling jobs and start the scheduler.
    Shutdown: stop the scheduler gracefully.
    """
    async with async_session() as db:
        await sync_jobs(db)
    scheduler.start()
    logging.getLogger("servicepulse").info("Scheduler started")
    yield
    scheduler.shutdown(wait=False)
    logging.getLogger("servicepulse").info("Scheduler stopped")


app = FastAPI(
    title="ServicePulse",
    description="Uptime and latency monitoring API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router)
app.include_router(checks.router)
app.include_router(incidents.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

import os
from fastapi.staticfiles import StaticFiles

if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
