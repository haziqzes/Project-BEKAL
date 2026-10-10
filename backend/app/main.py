import asyncio
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.candidates import CandidateStore
from app.intake import router as intake_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = CandidateStore(Path(os.getenv("CANDIDATE_STORAGE_DIR", "../runtime-data/candidates")))
    store.prepare()
    app.state.candidate_store = store

    async def expire_candidates() -> None:
        while True:
            await asyncio.sleep(300)
            store.cleanup_expired()

    cleanup_task = asyncio.create_task(expire_candidates())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task
        store.clear()


app = FastAPI(title="BEKAL API", version="0.1.0", lifespan=lifespan)
app.include_router(intake_router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Report whether the API process can serve requests."""
    return {"status": "healthy", "service": "backend"}


@app.get("/api/health/db")
def database_health() -> dict[str, str]:
    """Check PostgreSQL without creating or changing any application data."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=503, detail="Database is not configured")

    engine = create_engine(database_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable") from exc
    finally:
        engine.dispose()

    return {"status": "healthy", "service": "postgres"}
