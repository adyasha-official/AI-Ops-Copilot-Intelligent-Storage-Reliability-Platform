from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Drive, Incident
from app.schemas.incident import IncidentCreate, IncidentOut, IncidentUpdate
from app.services import drive_service

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])


@router.get("", response_model=list[IncidentOut])
def list_incidents(status: str | None = Query(None, pattern="^(OPEN|IN_PROGRESS|RESOLVED)$"),
                   db: Session = Depends(get_db)):
    q = select(Incident).order_by(Incident.created_at.desc())
    if status:
        q = q.where(Incident.status == status)
    return db.scalars(q).all()


@router.post("", response_model=IncidentOut, status_code=201)
def create_incident(body: IncidentCreate, db: Session = Depends(get_db)):
    drive = db.get(Drive, body.drive_id)
    if not drive:
        raise HTTPException(404, "Drive not found")
    return drive_service.create_incident(db, drive, body.severity, body.description)


@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, body: IncidentUpdate, db: Session = Depends(get_db)):
    inc = db.get(Incident, incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    inc.status = body.status
    inc.resolved_at = datetime.now(timezone.utc) if body.status == "RESOLVED" else None
    db.commit()
    db.refresh(inc)
    return inc
