"""
Core database settings and functions
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session

_db_path = Path(__file__).parent / ".." / "data" / "main.db"
db_connection_str = f"sqlite:///{_db_path}"
_db_backend_engine = create_engine(db_connection_str)
_db_backend_session_factory = sessionmaker(bind=_db_backend_engine)
# This is a class that can be instantiated to get a thread-local session
_ScopedSession = scoped_session(_db_backend_session_factory)

# Declarative base for all SQLAlchemy models
Base = declarative_base()


class DatabaseSession:
    """
    Simple wrapper for using session with "with DatabaseSession() as ..."
    Creates a thread-local connection to the backend database.
    """

    def __init__(self) -> None:
        self.session: Session = _ScopedSession()

    def __enter__(self) -> Session:
        return self.session

    def __exit__(self, *args: Any) -> None:
        self.session.close()
