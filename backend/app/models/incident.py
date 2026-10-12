from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.drive import utcnow


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    drive_id: Mapped[int] = mapped_column(ForeignKey("drives.id"), index=True)
    severity: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(15), default="OPEN", index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    drive = relationship("Drive", back_populates="incidents")
