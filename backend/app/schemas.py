import datetime

from pydantic import BaseModel, HttpUrl


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

class EndpointCreate(BaseModel):
    url: HttpUrl
    name: str
    interval_seconds: int = 30


class EndpointUpdate(BaseModel):
    name: str | None = None
    url: HttpUrl | None = None
    interval_seconds: int | None = None
    is_active: bool | None = None


class EndpointRead(BaseModel):
    id: int
    url: str
    name: str
    interval_seconds: int
    is_active: bool
    created_at: datetime.datetime
    latest_status: int | None = None
    latest_response_time_ms: float | None = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Check
# ---------------------------------------------------------------------------

class CheckRead(BaseModel):
    id: int
    endpoint_id: int
    status_code: int | None
    response_time_ms: float | None
    error: str | None
    checked_at: datetime.datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Incident
# ---------------------------------------------------------------------------

class IncidentRead(BaseModel):
    id: int
    endpoint_id: int
    endpoint_name: str | None = None
    endpoint_url: str | None = None
    started_at: datetime.datetime
    resolved_at: datetime.datetime | None
    failure_count: int

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    total_endpoints: int
    active_endpoints: int
    active_incidents: int
    overall_uptime_pct: float
