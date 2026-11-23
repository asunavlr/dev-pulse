import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from sqlalchemy import select
from sqlalchemy.orm import Session

from devpulse.core.config import get_settings
from devpulse.db import get_db, initialize_database
from devpulse.models import CheckResult, Incident, Target
from devpulse.monitoring import run_check
from devpulse.scheduler import monitor_loop
from devpulse.schemas import CheckResponse, IncidentResponse, TargetCreate, TargetResponse
from devpulse.security import assert_public_target, require_api_key


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    settings = get_settings()
    scheduler = asyncio.create_task(monitor_loop()) if settings.scheduler_enabled else None
    try:
        yield
    finally:
        if scheduler:
            scheduler.cancel()
            try:
                await scheduler
            except asyncio.CancelledError:
                pass


app = FastAPI(
    title="DevPulse API",
    description="HTTP uptime monitoring, latency tracking and incident management.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(select(1))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    return {"status": "ready"}


@app.get("/metrics", include_in_schema=False, dependencies=[Depends(require_api_key)])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/targets", response_model=TargetResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_api_key)])
def create_target(payload: TargetCreate, db: Session = Depends(get_db)):
    settings = get_settings()
    try:
        assert_public_target(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    timeout = min(payload.timeout_seconds, settings.max_timeout_seconds)
    target = Target(
        name=payload.name.strip(),
        url=str(payload.url),
        timeout_seconds=timeout,
        latency_threshold_ms=payload.latency_threshold_ms,
    )
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


@app.get("/targets", response_model=list[TargetResponse], dependencies=[Depends(require_api_key)])
def list_targets(db: Session = Depends(get_db)):
    return db.scalars(select(Target).order_by(Target.id.desc())).all()


@app.get("/targets/{target_id}", response_model=TargetResponse, dependencies=[Depends(require_api_key)])
def get_target(target_id: int, db: Session = Depends(get_db)):
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@app.delete("/targets/{target_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_api_key)])
def delete_target(target_id: int, db: Session = Depends(get_db)):
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    db.delete(target)
    db.commit()
    return Response(status_code=204)


@app.post("/targets/{target_id}/check", response_model=CheckResponse, dependencies=[Depends(require_api_key)])
async def check_target(target_id: int, db: Session = Depends(get_db)):
    target = db.get(Target, target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found")
    return await run_check(db, target)


@app.get("/targets/{target_id}/checks", response_model=list[CheckResponse], dependencies=[Depends(require_api_key)])
def check_history(target_id: int, db: Session = Depends(get_db)):
    if db.get(Target, target_id) is None:
        raise HTTPException(status_code=404, detail="Target not found")
    limit = get_settings().check_history_limit
    return db.scalars(
        select(CheckResult).where(CheckResult.target_id == target_id)
        .order_by(CheckResult.checked_at.desc()).limit(limit)
    ).all()


@app.get("/incidents", response_model=list[IncidentResponse], dependencies=[Depends(require_api_key)])
def list_incidents(active: bool | None = None, db: Session = Depends(get_db)):
    statement = select(Incident).order_by(Incident.created_at.desc())
    if active is not None:
        statement = statement.where(Incident.active.is_(active))
    return db.scalars(statement).all()
