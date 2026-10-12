from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["OPEN", "IN_PROGRESS", "RESOLVED"]
Severity = Literal["LOW", "MEDIUM", "HIGH"]


class IncidentCreate(BaseModel):
    drive_id: int
    severity: Severity | None = None  # defaults to the drive's current risk level
    description: str = Field(default="", max_length=2000)


class IncidentUpdate(BaseModel):
    status: Status


class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    drive_id: int
    severity: str
    status: str
    description: str
    created_at: datetime
    resolved_at: datetime | None = None
