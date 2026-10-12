from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"
    __table_args__ = (Index("ix_telemetry_drive_ts", "drive_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    drive_id: Mapped[int] = mapped_column(ForeignKey("drives.id"))
    temperature: Mapped[float] = mapped_column(Float)
    reallocated_sectors: Mapped[int] = mapped_column(Integer)
    power_on_hours: Mapped[int] = mapped_column(Integer)
    seek_error_rate: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    drive = relationship("Drive", back_populates="telemetry")
