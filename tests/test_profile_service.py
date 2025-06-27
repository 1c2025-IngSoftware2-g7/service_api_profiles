# tests/test_profile_service.py
import pytest
from unittest.mock import MagicMock, patch
from src.application.profile_service import ProfileService
from src.domain.profile import Profile
import os
from datetime import timedelta


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return ProfileService(mock_repo)


@pytest.fixture
def sample_profile_data():
    return {
        "uuid": "123e4567-e89b-12d3-a456-426614174000",
        "email": "test@example.com",
        "role": "student",
        "display_name": "Test User",
        "phone": "+1234567890",
        "location": "Test City",
        "birthday": "2000-01-01",
        "gender": "other",
        "description": "Test description",
        "display_image": "test.jpg"
    }

# Tests para create_profile


def test_create_profile_missing_fields(service):
    with pytest.raises(ValueError) as excinfo:
        service.create_profile({"email": "test@example.com"})
    assert "Missing required fields" in str(excinfo.value)


def test_create_profile_invalid_role(service):
    with pytest.raises(ValueError) as excinfo:
        service.create_profile({
            "uuid": "123",
            "email": "test@example.com",
            "role": "invalid_role"
        })
    assert "Invalid role" in str(excinfo.value)

# Tests para get_specific_profile


def test_get_specific_profile_not_found(service, mock_repo):
    mock_repo.get_profile.return_value = None
    assert service.get_specific_profile("123") is None
    mock_repo.get_profile.assert_called_once_with("123")

# Tests para modify_profile


def test_modify_profile_no_valid_fields(service, mock_repo):
    mock_repo.profile_exists.return_value = True
    with pytest.raises(ValueError) as excinfo:
        service.modify_profile("123", {"invalid_field": "value"})
    assert "No valid fields to update" in str(excinfo.value)


def test_modify_profile_protected_field(service, mock_repo):
    mock_repo.profile_exists.return_value = True
    with pytest.raises(ValueError) as excinfo:
        service.modify_profile("123", {"email": "new@example.com"})
    assert "Cannot modify protected field" in str(excinfo.value)

# Tests para add_image


@patch('google.cloud.storage.Client')
@patch('builtins.open', new_callable=MagicMock)
def test_add_image_success(MockOpen, MockClient, service, mock_repo):
    # Configurar mocks
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    MockClient.from_service_account_json.return_value.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.generate_signed_url.return_value = "http://example.com/image.jpg"

    # Configurar entorno
    os.environ['GOOGLE_CREDENTIALS_JSON'] = "{}"
    os.environ['GCS_BUCKET_NAME'] = "test-bucket"

    # Mock file
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_file.content_type = "image/jpeg"

    # Ejecutar
    url = service.add_image("123", mock_file)

    # Verificar
    assert url == "http://example.com/image.jpg"
    mock_blob.upload_from_file.assert_called_once()
    mock_blob.generate_signed_url.assert_called_once_with(
        version="v4",
        expiration=timedelta(minutes=15),
        method="GET"
    )

# Tests para edge cases


def test_modify_profile_not_found(service, mock_repo):
    mock_repo.profile_exists.return_value = False
    with pytest.raises(ValueError) as excinfo:
        service.modify_profile("123", {"display_name": "New Name"})
    assert "Profile not found" in str(excinfo.value)


def test_add_image_missing_env_vars(service):
    os.environ.pop('GOOGLE_CREDENTIALS_JSON', None)
    os.environ.pop('GCS_BUCKET_NAME', None)
    with pytest.raises(Exception):
        service.add_image("123", MagicMock())
