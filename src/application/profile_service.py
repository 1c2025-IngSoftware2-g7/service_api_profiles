from src.infrastructure.persistence.profiles_repository import ProfilesRepository
from src.domain.profile import Profile


class ProfileService:
    def __init__(self, profile_repository: ProfilesRepository, logger):
        self.log = logger
        self.profile_repository = profile_repository

    def create_profile(self, profile_data: dict):
        # Validación básica
        required_fields = ["uuid", "name",
                           "surname", "email", "password", "role"]
        missing_fields = [
            field for field in required_fields if field not in profile_data]
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}")

        # Verificar si el perfil ya existe
        if self.profile_repository.profile_exists(profile_data["uuid"]):
            raise ValueError("Profile already exists for this user")

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
            raise ValueError("Profile not found")

        # Actualizar en la base de datos
        return self.profile_repository.update_profile(uuid, updates)
