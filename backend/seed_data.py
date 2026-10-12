"""Generate 100 simulated drives with telemetry history.

Run:  python seed_data.py            (adds data only if the DB is empty)
      python seed_data.py --reset    (wipes and regenerates)
"""
import random
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.database import Base, SessionLocal, engine
from app.models import Drive, Incident, Telemetry
from app.services.drive_service import recompute_risk

N_DRIVES = 100
READINGS = 30            # one reading per day for 30 days
MODELS = ["Ironwolf-X4", "Barracuda-Q2", "Ultrastar-D8", "Exos-Z6"]


def seed(db, reset=False, seed_value=42) -> dict:
    if reset:
        for m in (Incident, Telemetry, Drive):
            db.query(m).delete()
        db.commit()
    if db.scalar(select(func.count()).select_from(Drive)):
        return {"seeded": False}

    rnd = random.Random(seed_value)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    # ~72 healthy, ~20 degrading, ~8 failing (matches the plan's example dashboard)
    profiles = ["healthy"] * 72 + ["degrading"] * 20 + ["failing"] * 8
    rnd.shuffle(profiles)

    drives, rows = [], 0
    for i, profile in enumerate(profiles, start=1):
        d = Drive(name=f"drive-{i:03d}", model=rnd.choice(MODELS),
                  serial_number=f"SN{rnd.randint(10**7, 10**8 - 1)}{i:03d}", status="ACTIVE")
        db.add(d)
        db.flush()
        base_temp = {"healthy": rnd.uniform(33, 42), "degrading": rnd.uniform(40, 48), "failing": rnd.uniform(48, 54)}[profile]
        end_temp = {"healthy": base_temp + rnd.uniform(-2, 3), "degrading": base_temp + rnd.uniform(6, 12), "failing": base_temp + rnd.uniform(9, 14)}[profile]
        end_sectors = {"healthy": rnd.randint(0, 25), "degrading": rnd.randint(80, 260), "failing": rnd.randint(300, 480)}[profile]
        hours0 = {"healthy": rnd.randint(2000, 30000), "degrading": rnd.randint(20000, 40000), "failing": rnd.randint(38000, 55000)}[profile]
        end_seek = {"healthy": rnd.uniform(2, 20), "degrading": rnd.uniform(25, 50), "failing": rnd.uniform(55, 90)}[profile]
        for r in range(READINGS):
            f = r / (READINGS - 1)
            db.add(Telemetry(
                drive_id=d.id,
                temperature=round(base_temp + (end_temp - base_temp) * f + rnd.gauss(0, 0.8), 1),
                reallocated_sectors=int(end_sectors * (f ** 1.6)),   # accelerating growth
                power_on_hours=hours0 + r * 24,
                seek_error_rate=round(max(0.0, end_seek * (0.4 + 0.6 * f) + rnd.gauss(0, 1.5)), 1),
                timestamp=now - timedelta(days=READINGS - 1 - r),
            ))
            rows += 1
        db.flush()
        recompute_risk(db, d)
        drives.append(d)
    db.commit()
    return {"seeded": True, "drives": len(drives), "telemetry_records": rows}


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        print(seed(session, reset="--reset" in sys.argv))
