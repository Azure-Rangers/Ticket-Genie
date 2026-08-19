"""Pytest configuration and automatic test database cleanup fixtures."""

import pytest
from database.connection import SessionLocal
from database.models_db import TicketDB


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_created_tickets():
    """Record pre-test ticket IDs and remove any new tickets created during test execution."""
    with SessionLocal() as db:
        initial_ids = {t.id for t in db.query(TicketDB.id).all()}

    yield

    with SessionLocal() as db:
        if initial_ids:
            new_tickets = db.query(TicketDB).filter(~TicketDB.id.in_(initial_ids)).all()
        else:
            new_tickets = db.query(TicketDB).all()
        for t in new_tickets:
            db.delete(t)
        db.commit()
