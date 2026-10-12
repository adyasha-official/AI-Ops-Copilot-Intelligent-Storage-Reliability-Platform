from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TelemetryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    temperature: float
    reallocated_sectors: int
    power_on_hours: int
    seek_error_rate: float
    timestamp: datetime


class DriveOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    model: str
    serial_number: str
    status: str
    risk_score: float
    risk_level: str
    created_at: datetime
    latest: TelemetryOut | None = None


class DriveList(BaseModel):
    total: int
    items: list[DriveOut]


class Stats(BaseModel):
    total_drives: int
    low: int
    medium: int
    high: int
    telemetry_records: int
    open_incidents: int
