import os
import sys
from pathlib import Path

# Use an isolated SQLite file; must be set before the app is imported.
os.environ["DATABASE_URL"] = "sqlite:///./test_ops.db"
os.environ["AUTO_SEED"] = "false"
os.environ["ANTHROPIC_API_KEY"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from seed_data import seed


@pytest.fixture(scope="session", autouse=True)
def _cleanup():
    yield
    engine.dispose()
    Path("test_ops.db").unlink(missing_ok=True)


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    with TestClient(app) as c:
        yield c
