from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from devpulse.db import Base

class Target(Base):
    __tablename__ = "targets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    timeout_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=5)
    latency_threshold_ms: Mapped[float] = mapped_column(Float, nullable=False, default=800)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    checks: Mapped[list["CheckResult"]] = relationship(back_populates="target", cascade="all, delete-orphan")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="target", cascade="all, delete-orphan")

class CheckResult(Base):
    __tablename__ = "check_results"
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id", ondelete="CASCADE"), nullable=False)
    is_up: Mapped[bool] = mapped_column(default=False, nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    target: Mapped[Target] = relationship(back_populates="checks")

class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("targets.id", ondelete="CASCADE"), nullable=False)
    kind: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    target: Mapped[Target] = relationship(back_populates="incidents")
