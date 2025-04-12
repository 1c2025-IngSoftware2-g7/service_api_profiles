from src.infrastructure.persistence.profiles_repository import ProfilesRepository
from src.domain.profile import Profile


class ProfileService:
    def __init__(self, profile_repository: ProfilesRepository, logger):
        self.log = logger
        self.profile_repository = profile_repository

    def create_profile(self, profile_data: dict):
        # Validar campos obligatorios
        required_fields = ['uuid', 'email', 'role']
        missing_fields = [
            field for field in required_fields if field not in profile_data]
        if missing_fields:
            raise ValueError(
                f"Missing required fields: {', '.join(missing_fields)}")

        # Validar roles permitidos
        valid_roles = ['student', 'teacher', 'admin']
        if profile_data.get('role') not in valid_roles:
            raise ValueError(
                f"Invalid role. Must be one of: {', '.join(valid_roles)}")

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

        # Campos permitidos para modificación
        allowed_fields = [
            'display_name', 'location', 'birthday',
            'gender', 'description', 'display_image'
        ]

        # Campos no modificables
        protected_fields = ['uuid', 'email', 'role']
        for field in protected_fields:
            if field in updates:
                raise ValueError(f"Cannot modify protected field: {field}")

        # Filtrar campos no permitidos
        updates = {k: v for k, v in updates.items() if k in allowed_fields}

        if not updates:
            raise ValueError("No valid fields to update")

        return self.profile_repository.update_profile(uuid, updates)
