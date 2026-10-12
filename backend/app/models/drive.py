from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Drive(Base):
    __tablename__ = "drives"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    model: Mapped[str] = mapped_column(String(50))
    serial_number: Mapped[str] = mapped_column(String(50), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    risk_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    risk_level: Mapped[str] = mapped_column(String(10), default="LOW", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    telemetry = relationship("Telemetry", back_populates="drive", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="drive", cascade="all, delete-orphan")
