import pytest
import requests
import uuid
import os
import time
from dotenv import load_dotenv
import io
from unittest.mock import patch

from src.app import profiles_app
from src.headers import BAD_REQUEST, PROFILE_NOT_FOUND

load_dotenv()


@pytest.fixture
def sample_profile_data():
    return {
        "uuid": str(uuid.uuid4()),
        "email": "test@example.com",
        "role": "student",
        "display_name": "Test User",
        "phone": "+1234567890",
    }


@pytest.fixture
def non_existent_profile_id():
    return str(uuid.uuid4())


@pytest.fixture
def bad_request_data():
    return {"invalid_field": "bad data"}


@pytest.fixture
def client():
    profiles_app.config['TESTING'] = True
    with profiles_app.test_client() as client:
        yield client

@pytest.fixture
def setup_test_profile(client, sample_profile_data):
    # Crear perfil de prueba
    response = client.post("/profiles", json=sample_profile_data)
    assert response.status_code == 201

    yield sample_profile_data["uuid"]  # Ejecutar los tests

    # Limpieza - eliminar perfil de prueba
    client.delete(f"/profiles/{sample_profile_data['uuid']}")


# Tests para endpoints públicos


# def test_get_public_profile(client, setup_test_profile):
#     profile_id = setup_test_profile
#     response = client.get(f"/profiles/public/{profile_id}")

#     assert response.status_code == 200
#     data = response.json["data"]
#     assert "display_name" in data
#     assert "phone" in data
#     assert "email" not in data  # Campo privado no debe aparecer

# # Tests para endpoints privados


# def test_get_private_profile(client, setup_test_profile):
#     profile_id = setup_test_profile
#     response = client.get(f"/profiles/{profile_id}")

#     assert response.status_code == 200
#     data = response.json["data"]
#     assert "email" in data  # Campo privado debe aparecer
#     assert "role" in data


# def test_create_profile(client, sample_profile_data):
#     response = client.post("/profiles", json=sample_profile_data)
#     assert response.status_code == 201
#     assert response.json["message"] == "Profile created successfully"

#     # Limpieza
#     client.delete(f"/profiles/{sample_profile_data['uuid']}")

# # Tests de errores


# def test_get_nonexistent_public_profile(client, non_existent_profile_id):
#     response = client.get(f"/profiles/public/{non_existent_profile_id}")
#     assert response.status_code == 404
#     assert response.json["title"] == PROFILE_NOT_FOUND


# def test_create_profile_bad_request(client, bad_request_data):
#     response = client.post("/profiles", json=bad_request_data)
#     assert response.status_code == 400
#     assert BAD_REQUEST in response.json["error"]


# def test_modify_profile(client, setup_test_profile):
#     profile_id = setup_test_profile
#     updates = {"display_name": "Updated Name"}

#     response = client.put(
#         "/profiles/modify",
#         json={"uuid": profile_id, "updates": updates}
#     )

#     assert response.status_code == 200
#     assert response.json["message"] == "Profile updated successfully"
#     assert response.json["data"]["updated_fields"] == updates

# # Test para verificar la salud del servicio


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


# def test_upload_image_success(client):
#     test_uuid = str(uuid.uuid4())
#     test_filename = f"{test_uuid}.jpg"
#     dummy_image = (io.BytesIO(b"fake-image-data"), test_filename)

#     with patch("app.storage_client") as mock_storage_client:
#         # Mock del bucket y blob
#         mock_bucket = mock_storage_client.bucket.return_value
#         mock_blob = mock_bucket.blob.return_value
#         mock_blob.public_url = f"https://fake-gcs/{test_filename}"

#         response = client.post(
#             "/upload",
#             data={
#                 "uuid": test_uuid,
#                 "image": (dummy_image[0], dummy_image[1])
#             },
#             content_type='multipart/form-data'
#         )

#         assert response.status_code == 200
#         data = response.get_json()
#         assert data["uuid"] == test_uuid
#         assert data["url"].startswith("https://fake-gcs/")
#         assert "Image uploaded" in data["message"]

