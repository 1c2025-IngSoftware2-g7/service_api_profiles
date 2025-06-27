# tests/api_test.py
import pytest
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify, Response
from src.domain.profile import Profile
from src.headers import (
    PROFILE_CREATED,
    PROFILE_NOT_FOUND,
    BAD_REQUEST,
    SERVER_ERROR,
    PROFILE_UPDATED
)

# Mockear todo antes de importar
with patch('src.infrastructure.persistence.base_entity.BaseEntity.connect_with_retries', return_value=MagicMock()), \
        patch('google.cloud.storage.Client', return_value=MagicMock()):
    from src.app import profiles_app

# Fixtures base


@pytest.fixture
def app():
    app = profiles_app
    app.config['TESTING'] = True
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_profile_data():
    return {
        "uuid": str(uuid.uuid4()),
        "email": "test@example.com",
        "role": "student",
        "display_name": "Test User",
        "phone": "+1234567890",
        "location": "Test Location",
        "birthday": "2000-01-01",
        "gender": "other",
        "description": "Test description",
        "display_image": "test.jpg"
    }


@pytest.fixture
def sample_profile_list(sample_profile_data):
    return [
        Profile(**sample_profile_data),
        Profile(**{**sample_profile_data, "uuid": str(uuid.uuid4()),
                "email": "test2@example.com"})
    ]

# Tests para endpoints de la API


class TestAPIEndpoints:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json == {"status": "ok"}

    def test_create_profile_success(self, app, client, sample_profile_data):
        with patch('src.app.profile_controller') as mock_controller:
            # Usamos app.app_context() para poder usar jsonify
            with app.app_context():
                mock_controller.create_profile.return_value = {
                    "response": jsonify({
                        "message": PROFILE_CREATED,
                        "data": sample_profile_data
                    }),
                    "code_status": 201
                }

            response = client.post("/profiles", json=sample_profile_data)
            assert response.status_code == 201
            assert response.json["message"] == PROFILE_CREATED

    def test_get_all_profiles_success(self, app, client, sample_profile_list):
        with patch('src.app.profile_controller') as mock_controller:
            # Preparar datos de respuesta
            response_data = [{
                "uuid": p.uuid,
                "email": p.email,
                "role": p.role,
                "display_name": p.display_name,
                "phone": p.phone
            } for p in sample_profile_list]

            # Usamos app.app_context() para poder usar jsonify
            with app.app_context():
                mock_controller.get_all_profiles.return_value = {
                    "response": jsonify({"data": response_data}),
                    "code_status": 200
                }

            response = client.get("/profiles")
            assert response.status_code == 200
            assert len(response.json["data"]) == 2

# [Mantener el resto de los tests...]

# Tests para ProfileService


class TestProfileService:
    @patch('src.infrastructure.persistence.profiles_repository.ProfilesRepository')
    def test_get_all_profiles_success(self, mock_repo, sample_profile_list):
        """Test para obtener todos los perfiles desde el servicio"""
        from src.application.profile_service import ProfileService

        mock_repo.return_value.get_profiles.return_value = sample_profile_list
        service = ProfileService(mock_repo.return_value)

        result = service.get_all_profiles()
        assert len(result) == 2
        assert isinstance(result[0], Profile)

    @patch('src.infrastructure.persistence.profiles_repository.ProfilesRepository')
    def test_get_all_profiles_empty(self, mock_repo):
        """Test para lista vacía de perfiles"""
        from src.application.profile_service import ProfileService

        mock_repo.return_value.get_profiles.return_value = []
        service = ProfileService(mock_repo.return_value)

        result = service.get_all_profiles()
        assert result == []

# Tests para ProfilesRepository


class TestProfilesRepository:
    @patch('psycopg.connect')
    def test_get_profiles_success(self, mock_connect, sample_profile_data):
        """Test para obtener perfiles desde el repositorio"""
        from src.infrastructure.persistence.profiles_repository import ProfilesRepository

        # Configurar mock con todos los campos requeridos
        complete_data = {
            **sample_profile_data,
            "location": "Test Location",
            "birthday": "2000-01-01",
            "gender": "other",
            "description": "Test description",
            "display_image": "test.jpg"
        }

        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            tuple(complete_data.values()),
            tuple({**complete_data, "uuid": str(uuid.uuid4())}.values())
        ]
        mock_cursor.description = [(k,) for k in complete_data.keys()]

        repo = ProfilesRepository()
        result = repo.get_profiles()

        assert len(result) == 2
        assert isinstance(result[0], Profile)
        mock_cursor.execute.assert_called_once_with(
            "SELECT * FROM profiles", ())

    @patch('psycopg.connect')
    def test_get_profiles_empty(self, mock_connect):
        """Test para repositorio vacío"""
        from src.infrastructure.persistence.profiles_repository import ProfilesRepository

        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = []

        repo = ProfilesRepository()
        result = repo.get_profiles()

        assert result == []

# Tests para ProfileController


class TestProfileController:
    def test_get_all_profiles_success(self, app, sample_profile_list):
        """Test para controlador obteniendo perfiles"""
        from src.presentation.profile_controller import ProfileController
        from src.application.profile_service import ProfileService

        with app.app_context():
            mock_service = MagicMock(spec=ProfileService)
            mock_service.get_all_profiles.return_value = sample_profile_list

            controller = ProfileController(mock_service)
            result = controller.get_all_profiles()

            assert result["code_status"] == 200
            assert len(result["response"].json["data"]) == 2

    def test_get_all_profiles_error(self, app):
        """Test para error en controlador"""
        from src.presentation.profile_controller import ProfileController
        from src.application.profile_service import ProfileService

        with app.app_context():
            mock_service = MagicMock(spec=ProfileService)
            mock_service.get_all_profiles.side_effect = Exception("DB Error")

            controller = ProfileController(mock_service)
            result = controller.get_all_profiles()

            assert result["code_status"] == 500
            assert "Internal server error" in result["response"].json["detail"]
