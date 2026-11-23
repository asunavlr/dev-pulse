import asyncio
import logging

from sqlalchemy import select

from devpulse.core.config import get_settings
from devpulse.db import SessionLocal
from devpulse.models import Target
from devpulse.monitoring import run_check

logger = logging.getLogger(__name__)


async def monitor_loop() -> None:
    settings = get_settings()
    while True:
        try:
            with SessionLocal() as db:
                targets = db.scalars(
                    select(Target).order_by(Target.id).limit(settings.max_targets_per_cycle)
                ).all()
                for target in targets:
                    await run_check(db, target)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled monitoring cycle failed")
        await asyncio.sleep(settings.check_interval_seconds)
