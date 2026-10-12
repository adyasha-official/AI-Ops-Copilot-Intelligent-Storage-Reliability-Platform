"""Shared DB helpers used by both the REST routes and the copilot tools."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Drive, Incident, Telemetry
from app.services.risk_engine import calculate_risk


def latest_telemetry(db: Session, drive_id: int) -> Telemetry | None:
    return db.scalars(
        select(Telemetry).where(Telemetry.drive_id == drive_id)
        .order_by(Telemetry.timestamp.desc()).limit(1)
    ).first()


def history(db: Session, drive_id: int, limit: int = 100) -> list[Telemetry]:
    rows = db.scalars(
        select(Telemetry).where(Telemetry.drive_id == drive_id)
        .order_by(Telemetry.timestamp.desc()).limit(limit)
    ).all()
    return list(reversed(rows))


def recompute_risk(db: Session, drive: Drive) -> Drive:
    t = latest_telemetry(db, drive.id)
    if t:
        drive.risk_score, drive.risk_level = calculate_risk(
            t.temperature, t.reallocated_sectors, t.power_on_hours, t.seek_error_rate
        )
    return drive


def attach_latest(db: Session, drives: list[Drive]) -> list[Drive]:
    """Attach the latest telemetry row to each drive (single query, no N+1)."""
    ids = [d.id for d in drives]
    if not ids:
        return drives
    sub = (select(Telemetry.drive_id, func.max(Telemetry.timestamp).label("ts"))
           .where(Telemetry.drive_id.in_(ids)).group_by(Telemetry.drive_id).subquery())
    rows = db.scalars(select(Telemetry).join(
        sub, (Telemetry.drive_id == sub.c.drive_id) & (Telemetry.timestamp == sub.c.ts))).all()
    by_drive = {r.drive_id: r for r in rows}
    for d in drives:
        d.latest = by_drive.get(d.id)
    return drives


def create_incident(db: Session, drive: Drive, severity: str | None, description: str) -> Incident:
    inc = Incident(drive_id=drive.id, severity=severity or drive.risk_level, description=description)
    db.add(inc)
    db.commit()
    db.refresh(inc)
    return inc
