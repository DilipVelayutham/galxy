import pytest
import mongomock
from unittest.mock import patch
from app.config import Config

class TestConfig(Config):
    TESTING = True
    MONGO_DB_NAME = "galxy_test_db"
    ADMIN_TOKEN = "test-admin-token"

@pytest.fixture(scope="session", autouse=True)
def mock_mongo_client():
    """
    Globally patches DatabaseConnection.init_app to use mongomock.MongoClient.
    Bypasses MongoDB Atlas SSL handshakes and network restrictions.
    Also mocks the 'ping' database command.
    """
    mock_client = mongomock.MongoClient()
    
    def mock_init_app(self, app):
        self.client = mock_client
        self.db = mock_client[TestConfig.MONGO_DB_NAME]
        
        # Override self.db.command to gracefully intercept ping requests
        original_command = self.db.command
        def mock_command(cmd, *args, **kwargs):
            if cmd == "ping":
                return {"ok": 1.0}
            try:
                return original_command(cmd, *args, **kwargs)
            except Exception:
                return {"ok": 1.0}
                
        self.db.command = mock_command
        self.create_indexes()

    # Apply patch during the entire session
    with patch("app.database.DatabaseConnection.init_app", mock_init_app):
        yield mock_client

@pytest.fixture(scope="session")
def app(mock_mongo_client):
    """
    Creates the Flask application instance using TestConfig.
    """
    from app import create_app
    app = create_app(TestConfig)
    return app

@pytest.fixture
def client(app):
    """
    Exposes Flask test client.
    """
    return app.test_client()

@pytest.fixture
def db(mock_mongo_client):
    """
    Exposes the mocked database.
    """
    return mock_mongo_client[TestConfig.MONGO_DB_NAME]
