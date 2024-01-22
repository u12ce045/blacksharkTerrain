"""Copyright (C) 2015-2021 Blackshark.ai GmbH. All Rights reserved. www.blackshark.ai"""
import logging
import sqlite3
from typing import Generator
from unittest.case import TestCase

import pytest
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.session import Session

import models.database
from models.database import Base


logging.basicConfig()
# Caution:
# when using FastAPI's TestClient the request is issued in a separate thread
# this causes an exception, when the DB connection is closed, despite
# specifying that sqlite is shared, and checks for same thread should be omitted.
# Hence, just disable Exception message here.
# Could mask nasty errors!?
logging.getLogger("sqlalchemy.pool.impl.SingletonThreadPool").disabled = True


@pytest.fixture
def database() -> Generator[None, None, None]:
    """
    This sets up an in-memory test DB, sets up the tables, and patches the ScopedSession
    so that code using the DB is automatically using the test DB.
    """
    creator = lambda: sqlite3.connect("file::memory:?cache=shared", uri=True)
    db_engine = create_engine("sqlite://", creator=creator, connect_args={"check_same_thread": False})
    session_factory = sessionmaker(bind=db_engine)

    def test_db_session() -> Session:
        """Used as session factory during test cases"""
        return scoped_session(session_factory)

    # overwrite/patch Session with connection to test DB
    # must be done directly with imported symbol of module module.database!
    models.database.__dict__["_ScopedSession"] = test_db_session
    # setup all tables
    # Note that if there are special migrations not reflected in the models,
    # then create_all() might not produce an identical duplicate of the production DB schema.
    test_db_connection = db_engine.connect()
    Base.metadata.create_all(test_db_connection)

    yield None  # hand control over to pytest

    # rollback, close and be done with it
    test_db_connection.close()
    db_engine.dispose()


@pytest.fixture(scope="function")
def check() -> TestCase:
    """Returns a TestCase class so that we can easily use its assert* functions"""
    return TestCase()
