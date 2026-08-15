import os
import urllib.parse
from typing import Any, Dict, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from database.models_db import Base

# Azure SQL / Environment config
DATABASE_URL = os.getenv("DATABASE_URL")
DB_SERVER = os.getenv("DB_SERVER", "")
DB_NAME = os.getenv("DB_NAME", "TicketGenieDB")
DB_USER = os.getenv("DB_USER", "sqladmin")
DB_PASSWORD = os.getenv("DB_ADMIN_PASSWORD") or os.getenv("DB_PASSWORD", "")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")

IS_AZURE_CONFIGURED = bool(DATABASE_URL or (DB_SERVER and DB_PASSWORD))


def _get_sqlalchemy_url() -> str:
    if DATABASE_URL:
        # If DATABASE_URL is already an mssql or pyodbc string
        if DATABASE_URL.startswith("mssql"):
            return DATABASE_URL
        # If raw ADO.NET / ODBC style string: "Server=tcp:...;Database=...;..."
        params = urllib.parse.quote_plus(DATABASE_URL)
        return f"mssql+pyodbc:///?odbc_connect={params}"

    if DB_SERVER and DB_PASSWORD:
        driver = DB_DRIVER.replace(" ", "+")
        is_port_in_server = "," in DB_SERVER or ":" in DB_SERVER
        server_str = DB_SERVER if is_port_in_server else f"{DB_SERVER},{DB_PORT}"
        user_str = urllib.parse.quote_plus(DB_USER)
        pwd_str = urllib.parse.quote_plus(DB_PASSWORD)
        return (
            f"mssql+pyodbc://{user_str}:{pwd_str}@{server_str}/{DB_NAME}"
            f"?driver={driver}&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
        )

    # Fallback to local SQLite database when Azure DB is not configured
    return "sqlite:///./ticketgenie.db"


def create_db_engine():
    db_url = _get_sqlalchemy_url()
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    try:
        engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"⚠️ Primary DB connection ({db_url.split('@')[-1]}) failed: {e}")
        print("💡 Falling back to local SQLite engine...")
        fallback_url = "sqlite:///./ticketgenie.db"
        return create_engine(
            fallback_url, connect_args={"check_same_thread": False}, pool_pre_ping=True
        )


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db_schema():
    """Create database tables if they do not exist and ensure missing columns are added."""
    try:
        Base.metadata.create_all(bind=engine)
        # Handle SQLite column additions gracefully if table pre-existed
        if engine.dialect.name == "sqlite":
            with engine.connect() as conn:
                existing_cols = [r[1] for r in conn.execute(text("PRAGMA table_info(tickets)")).fetchall()]
                if "queue" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN queue VARCHAR(100) DEFAULT 'IT - Service Desk'"))
                if "parent_ticket_id" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN parent_ticket_id VARCHAR(50)"))
                if "auto_resolved" not in existing_cols:
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN auto_resolved BOOLEAN DEFAULT 0"))
                conn.commit()
    except Exception as e:
        print(f"⚠️ Error creating database schema: {e}")


def get_db_config() -> Dict[str, Any]:
    """Return configured database connection parameters."""
    return {
        "server": DB_SERVER or "Azure SQL",
        "database": DB_NAME,
        "user": DB_USER,
        "password": "***" if DB_PASSWORD else None,
        "is_configured": IS_AZURE_CONFIGURED,
        "dialect": engine.dialect.name,
    }


def check_db_health() -> bool:
    """Check connection status for database backend."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db() -> Generator[Session, None, None]:
    """Dependency injection provider for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
