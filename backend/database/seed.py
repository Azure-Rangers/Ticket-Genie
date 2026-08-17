"""Database Seeding Module for TicketGenie.

Loads and executes seed statements directly from SQL seed files.
"""

from pathlib import Path
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.connection import engine

SEED_SQL_FILE = Path(__file__).resolve().parent.parent.parent / "database" / "seed_data.sql"


def seed_initial_data(db: Optional[Session] = None) -> None:
    """Execute SQL seed script to populate initial database records cleanly."""
    if not SEED_SQL_FILE.exists():
        print(f"⚠️ Seed SQL file not found at {SEED_SQL_FILE}")
        return

    with engine.connect() as conn:
        try:
            sql_content = SEED_SQL_FILE.read_text(encoding="utf-8")
            raw_blocks = sql_content.split(";")
            for block in raw_blocks:
                lines = [line for line in block.splitlines() if not line.strip().startswith("--")]
                stmt = "\n".join(lines).strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
            print(f"✅ Executed SQL seed script from {SEED_SQL_FILE.name}.")
        except Exception as e:
            print(f"⚠️ Error executing SQL seed script: {e}")
