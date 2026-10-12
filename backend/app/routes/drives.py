from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Drive, Incident, Telemetry
from app.schemas.drive import DriveList, DriveOut, Stats, TelemetryOut
from app.services import drive_service

router = APIRouter(prefix="/api/v1", tags=["drives"])


@router.get("/stats", response_model=Stats)
def stats(db: Session = Depends(get_db)):
    counts = dict(db.execute(select(Drive.risk_level, func.count()).group_by(Drive.risk_level)).all())
    return Stats(
        total_drives=sum(counts.values()),
        low=counts.get("LOW", 0), medium=counts.get("MEDIUM", 0), high=counts.get("HIGH", 0),
        telemetry_records=db.scalar(select(func.count()).select_from(Telemetry)) or 0,
        open_incidents=db.scalar(select(func.count()).select_from(Incident)
                                 .where(Incident.status != "RESOLVED")) or 0,
    )


@router.get("/drives", response_model=DriveList)
def list_drives(
    risk_level: str | None = Query(None, pattern="^(LOW|MEDIUM|HIGH)$"),
    search: str | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = select(Drive)
    if risk_level:
        q = q.where(Drive.risk_level == risk_level)
    if search:
        q = q.where(Drive.name.ilike(f"%{search}%"))
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    drives = db.scalars(q.order_by(Drive.risk_score.desc(), Drive.id).limit(limit).offset(offset)).all()
    return DriveList(total=total, items=drive_service.attach_latest(db, list(drives)))


# NOTE: must be declared before /drives/{drive_id}
@router.get("/drives/at-risk", response_model=list[DriveOut])
def at_risk(min_level: str = Query("MEDIUM", pattern="^(MEDIUM|HIGH)$"), db: Session = Depends(get_db)):
    levels = ["HIGH"] if min_level == "HIGH" else ["MEDIUM", "HIGH"]
    drives = db.scalars(select(Drive).where(Drive.risk_level.in_(levels))
                        .order_by(Drive.risk_score.desc())).all()
    return drive_service.attach_latest(db, list(drives))


@router.get("/drives/{drive_id}", response_model=DriveOut)
def get_drive(drive_id: int, db: Session = Depends(get_db)):
    drive = db.get(Drive, drive_id)
    if not drive:
        raise HTTPException(404, "Drive not found")
    return drive_service.attach_latest(db, [drive])[0]


@router.get("/drives/{drive_id}/history", response_model=list[TelemetryOut])
def drive_history(drive_id: int, limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    if not db.get(Drive, drive_id):
        raise HTTPException(404, "Drive not found")
    return drive_service.history(db, drive_id, limit)
