from google.cloud import storage
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

from src.infrastructure.persistence.profiles_repository import ProfilesRepository
from src.logger_config import get_logger

logger = get_logger("api-profiles")

class ProfileService:
    def __init__(self, profile_repository: ProfilesRepository):
        self.profile_repository = profile_repository

    def create_profile(self, profile_data: dict):
        # Validar campos obligatorios
        required_fields = ["uuid", "email", "role"]
        missing_fields = [
            field for field in required_fields if field not in profile_data
        ]
        if missing_fields:
            logger.info(f"[SERVICE] Missing required fields.")
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validar roles permitidos
        valid_roles = ["student", "teacher", "admin"]
        if profile_data.get("role") not in valid_roles:
            logger.info(f"[SERVICE] Invalid role.")
            raise ValueError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")

        if self.profile_repository.profile_exists(profile_data["uuid"]):
            logger.info(f"[SERVICE] Profile already exists for this user.")
            raise ValueError("Profile already exists for this user.")

        # Insertar en la base de datos
        return self.profile_repository.insert_profile(profile_data)

    def get_specific_profile(self, uuid):
        profile = self.profile_repository.get_profile(uuid)
        if not profile:
            return None
        return profile

    def modify_profile(self, uuid, updates):
        # Validar que el perfil exista
        if not self.profile_repository.profile_exists(uuid):
            logger.warn(f"[SERVICE] Profile not found.")
            raise ValueError("Profile not found.")

        # Campos permitidos para modificación
        allowed_fields = [
            "display_name",
            "location",
            "birthday",
            "gender",
            "description",
            "display_image",
            "phone",
        ]

        # Campos no modificables
        protected_fields = ["uuid", "email", "role"]
        for field in protected_fields:
            if field in updates:
                logger.warn(f"[SERVICE] Cannot modify protected field: {field}.")
                raise ValueError(f"Cannot modify protected field: {field}")

        # Filtrar campos no permitidos
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if not updates:
            logger.warn(f"[SERVICE] Cannot modify protected field: {field}.")
            raise ValueError("No valid fields to update")

        return self.profile_repository.update_profile(uuid, updates)

    def add_image(self, uuid, file):
        """Save the image to GCP."""
        bucket = self._get_gcp_bucket()
        ext = os.path.splitext(file.filename)[1]  # Extract extension (.jpg, .png, etc.)
        filename = f"{uuid}{ext}"
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type=file.content_type)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="GET",
        )
        return url

    def _get_gcp_bucket(self):
        # Reconstruct JSON file from environment variable:
        credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        json_path = '/tmp/gcs-key.json'
        with open(json_path, 'w') as f:
            f.write(credentials_json)

        # Initialize GCS:
        storage_client = storage.Client.from_service_account_json(json_path)
        bucket = storage_client.bucket(os.getenv('GCS_BUCKET_NAME'))
        return bucket
