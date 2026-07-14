import os
import pytest
from fastapi.testclient import TestClient

# We monkeypatch the STATE_FILE in db_manager before any other imports
import db_manager
db_manager.STATE_FILE = "test_l200_state.json"

from db_manager import DBManager
import main
from main import app

@pytest.fixture(autouse=True)
def clean_test_env(monkeypatch):
    """
    Fixture that runs before each test to clean up any test state files
    and mock Firestore.
    """
    # Force state file to be the test state file
    monkeypatch.setattr(db_manager, "STATE_FILE", "test_l200_state.json")
    
    # Mock Firestore db to ensure tests run in local-only fallback mode
    monkeypatch.setattr(DBManager, "firestore_db", None)
    
    # Remove test file if it exists from previous run
    if os.path.exists("test_l200_state.json"):
        try:
            os.remove("test_l200_state.json")
        except OSError:
            pass
            
    yield
    
    # Clean up after test
    if os.path.exists("test_l200_state.json"):
        try:
            os.remove("test_l200_state.json")
        except OSError:
            pass

@pytest.fixture
def db_mgr():
    """Provides a clean DBManager instance using the test state file."""
    # Reset internal Firestore client cache and return a fresh manager
    manager = DBManager()
    return manager

@pytest.fixture
def client(monkeypatch):
    """Provides a FastAPI test client with mocked DBManager."""
    # Ensure main's db uses local test state file
    monkeypatch.setattr(main.db, "_firestore_client_cache", None)
    # Return TestClient
    return TestClient(app)
