from src.infrastructure.config.db_config import DatabaseConfig
from src.infrastructure.persistence.base_entity import BaseEntity
from src.domain.profile import Profile
from werkzeug.security import generate_password_hash


class ProfilesRepository(BaseEntity):
    def __init__(self, logger):
        self.log = logger
        super().__init__()

    def _parse_profile(self, profile_data):
        """Convierte datos de la base de datos a objeto Profile"""
        return Profile(
            uuid=profile_data["uuid"],
            name=profile_data["name"],
            surname=profile_data["surname"],
            email=profile_data["email"],
            password=profile_data["password"],
            role=profile_data["role"],
            location=profile_data.get("location"),
            profile_picture=profile_data.get("profile_picture")
        )

    def profile_exists(self, profile_uuid: str) -> bool:
        """Verifica si un perfil ya existe"""
        query = "SELECT 1 FROM profiles WHERE uuid = %s LIMIT 1"
        params = (str(profile_uuid),)
        self.cursor.execute(query, params)
        return bool(self.cursor.fetchone())

    def insert_profile(self, profile_data: dict):
        """Inserta un nuevo perfil en la base de datos"""
        query = """
        INSERT INTO profiles (
            uuid, name, surname, email, 
            password, role, location, profile_picture
        ) VALUES (
            %(uuid)s, %(name)s, %(surname)s, %(email)s,
            %(password)s, %(role)s, %(location)s, %(profile_picture)s
        )
        """

        # Hashear la contraseña
        profile_data["password"] = generate_password_hash(
            profile_data["password"])

        self.cursor.execute(query, profile_data)
        self.conn.commit()

        return self._parse_profile(profile_data)
