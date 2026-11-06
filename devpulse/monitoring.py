import time
from datetime import datetime, timezone
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session
from devpulse.metrics import CHECKS_TOTAL, CHECK_DURATION, TARGET_UP
from devpulse.models import CheckResult, Incident, Target

async def run_check(db: Session, target: Target) -> CheckResult:
    started = time.perf_counter()
    status_code = None
    error = None
    try:
        async with httpx.AsyncClient(
            timeout=target.timeout_seconds,
            follow_redirects=False,
            headers={"User-Agent": "DevPulse-Monitor/0.1"},
        ) as client:
            response = await client.get(target.url)
            status_code = response.status_code
            is_up = 200 <= response.status_code < 400
            if not is_up:
                error = f"Unexpected HTTP status: {response.status_code}"
    except httpx.TimeoutException:
        is_up = False
        error = "Request timed out"
    except httpx.HTTPError as exc:
        is_up = False
        error = f"HTTP request failed: {type(exc).__name__}"

    latency = (time.perf_counter() - started) * 1000
    result = CheckResult(
        target_id=target.id,
        is_up=is_up,
        status_code=status_code,
        latency_ms=round(latency, 2),
        error=error,
    )
    db.add(result)

    active = db.scalars(
        select(Incident).where(Incident.target_id == target.id, Incident.active.is_(True))
    ).all()
    kind = "availability" if not is_up else (
        "latency" if latency > target.latency_threshold_ms else None
    )
    if kind:
        message = error or f"Latency {latency:.2f}ms exceeded {target.latency_threshold_ms:.2f}ms"
        existing = next((incident for incident in active if incident.kind == kind), None)
        if existing is None:
            db.add(Incident(target_id=target.id, kind=kind, message=message, active=True))
    else:
        for incident in active:
            if incident.kind == "availability" or (incident.kind == "latency" and is_up):
                incident.active = False
                incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(result)
    label = "up" if is_up else "down"
    CHECKS_TOTAL.labels(target=target.name, status=label).inc()
    CHECK_DURATION.labels(target=target.name).observe(latency / 1000)
    TARGET_UP.labels(target=target.name).set(1 if is_up else 0)
    return result
