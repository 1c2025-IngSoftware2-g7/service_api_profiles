# tests/test_profile_controller.py
import pytest
from unittest.mock import MagicMock, patch
from flask import jsonify
from src.presentation.profile_controller import ProfileController
from src.application.profile_service import ProfileService
from src.domain.profile import Profile
from src.headers import (
    PROFILE_CREATED,
    PROFILE_NOT_FOUND,
    BAD_REQUEST,
    SERVER_ERROR,
    PROFILE_UPDATED,
    PROFILE_ALREADY_EXISTS,
    INVALID_FIELD
)


@pytest.fixture
def mock_service():
    return MagicMock(spec=ProfileService)


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


def test_create_profile_success(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = sample_profile_data
    mock_service.create_profile.return_value = Profile(**sample_profile_data)

    result = controller.create_profile(mock_request)

    assert result["code_status"] == 201
    assert PROFILE_CREATED in str(result["response"].data)
    mock_service.create_profile.assert_called_once_with(sample_profile_data)


def test_create_profile_invalid_json(mock_service):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.is_json = False

    result = controller.create_profile(mock_request)

    assert result["code_status"] == 400
    assert BAD_REQUEST in str(result["response"].data)


def test_create_profile_existing_user(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = sample_profile_data
    mock_service.create_profile.side_effect = ValueError(
        "Profile already exists for this user")

    result = controller.create_profile(mock_request)

    assert result["code_status"] == 400
    assert "Profile already exists" in str(result["response"].data)

# Tests para get_specific_profiles


def test_get_private_profile_success(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    profile = Profile(**sample_profile_data)
    mock_service.get_specific_profile.return_value = profile

    result = controller.get_specific_profiles(profile.uuid, public_view=False)

    assert result["code_status"] == 200
    # Email visible en vista privada
    assert profile.email in str(result["response"].data)


def test_get_public_profile_success(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    profile = Profile(**sample_profile_data)
    mock_service.get_specific_profile.return_value = profile

    result = controller.get_specific_profiles(profile.uuid, public_view=True)

    assert result["code_status"] == 200
    # Email no visible en vista pública
    assert profile.email not in str(result["response"].data)


def test_get_profile_not_found(mock_service):
    controller = ProfileController(mock_service)
    mock_service.get_specific_profile.return_value = None

    result = controller.get_specific_profiles(
        "invalid-uuid", public_view=False)

    assert result["code_status"] == 404
    assert PROFILE_NOT_FOUND in str(result["response"].data)

# Tests para get_all_profiles


def test_get_all_profiles_success(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    profiles = [
        Profile(**sample_profile_data),
        Profile(**{**sample_profile_data, "uuid": "456",
                "email": "test2@example.com"})
    ]
    mock_service.get_all_profiles.return_value = profiles

    result = controller.get_all_profiles()

    assert result["code_status"] == 200
    assert len(result["response"].json["data"]) == 2


def test_get_all_profiles_empty(mock_service):
    controller = ProfileController(mock_service)
    mock_service.get_all_profiles.return_value = []

    result = controller.get_all_profiles()

    assert result["code_status"] == 200
    assert len(result["response"].json["data"]) == 0

# Tests para modify_profile


def test_modify_profile_success(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.is_json = True
    updates = {"display_name": "New Name"}
    mock_request.get_json.return_value = {
        "uuid": sample_profile_data["uuid"],
        "updates": updates
    }
    updated_profile = Profile(
        **{**sample_profile_data, "display_name": "New Name"})
    mock_service.modify_profile.return_value = updated_profile

    result = controller.modify_profile(mock_request)

    assert result["code_status"] == 200
    assert PROFILE_UPDATED in str(result["response"].data)
    assert "New Name" in str(result["response"].data)


def test_modify_profile_invalid_field(mock_service, sample_profile_data):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "uuid": sample_profile_data["uuid"],
        "updates": {"invalid_field": "value"}
    }
    mock_service.modify_profile.side_effect = ValueError(
        "Field 'invalid_field' cannot be modified")

    result = controller.modify_profile(mock_request)

    assert result["code_status"] == 400
    response_data = result["response"].get_json()
    assert response_data["error"] == "Field 'invalid_field' cannot be modified"


def test_modify_profile_not_found(mock_service):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "uuid": "invalid-uuid",
        "updates": {"display_name": "New Name"}
    }
    mock_service.modify_profile.side_effect = ValueError("Profile not found")

    result = controller.modify_profile(mock_request)

    # El controlador actual devuelve 400, no 404
    assert result["code_status"] == 400
    assert "Profile not found" in str(result["response"].data)

# Tests para upload_image


def test_upload_image_success(mock_service):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.form = {"uuid": "123"}
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_request.files = {"image": mock_file}
    mock_service.add_image.return_value = "http://example.com/image.jpg"

    result = controller.upload_image(mock_request)

    assert result["code_status"] == 200
    assert "image.jpg" in str(result["response"].data)


def test_upload_image_missing_uuid(mock_service):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.form = {}
    mock_request.files = {"image": MagicMock()}

    result = controller.upload_image(mock_request)

    assert result["code_status"] == 400
    assert "UUID are required" in str(result["response"].data)


def test_upload_image_missing_file(mock_service):
    controller = ProfileController(mock_service)
    mock_request = MagicMock()
    mock_request.form = {"uuid": "123"}
    mock_request.files = {}

    result = controller.upload_image(mock_request)

    assert result["code_status"] == 400
    assert "Missing image or UUID" in str(result["response"].data)

