# tests/conftest.py
import pytest
from unittest.mock import patch, MagicMock
import os

# Mock para la conexión a la base de datos


@pytest.fixture(autouse=True)
def mock_db_connection():
    with patch("src.infrastructure.persistence.base_entity.psycopg.connect") as mock_connect:
        # Configurar mock de conexión y cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield

# Mock para Google Cloud Storage


@pytest.fixture(autouse=True)
def mock_gcs():
    with patch("google.cloud.storage.Client"):
        yield

# Configurar variables de entorno para testing


@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ['DB_NAME'] = "test_db"
    os.environ['DB_USER'] = "test_user"
    os.environ['DB_PASSWORD'] = "test_pass"
    os.environ['DB_HOST'] = "localhost"
    os.environ['DB_PORT'] = "5432"
    os.environ['GCS_BUCKET_NAME'] = "test-bucket"
    os.environ['GOOGLE_CREDENTIALS_JSON'] = "{}"
    os.environ['SECRET_KEY_SESSION'] = "test-secret-key"

# Fixture para la aplicación Flask


@pytest.fixture
def app():
    # Mockear todo antes de importar la app
    with patch("src.infrastructure.persistence.base_entity.BaseEntity.connect_with_retries"), \
            patch("google.cloud.storage.Client"):
        from src.app import profiles_app
        app = profiles_app
        app.config['TESTING'] = True
        yield app

# Fixture para el cliente de pruebas


@pytest.fixture
def client(app):
    return app.test_client()

# Contexto de aplicación automático


@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        yield
