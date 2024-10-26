import pytest
from models import database
from server import create_app
import os
import shutil


def pytest_sessionstart(session):
    shutil.copy('database.db', 'database.db.bak')


@pytest.fixture
def app():
    app = create_app()
    return app


def pytest_sessionfinish(session, exitstatus):
    print("\nCleaning up")
    database.db.close()
    os.remove('database.db')
    os.rename('database.db.bak', 'database.db')
