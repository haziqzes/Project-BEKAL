import os

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI(title="BEKAL API", version="0.1.0")


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
