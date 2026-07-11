import os
import pytest
import sqlite3
import tempfile

from app import app as flask_app
from init_db import init_db

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)


    # Pass the database path to our Flask app via config
    flask_app.config.update({
        "TESTING": True,
        "DATABASE_PATH": db_path,
    })

    # Run the initial DB schema and populate dummy data on the test DB
    init_db(db_path)

    yield flask_app
    
    # Cleanup after test finishes
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
