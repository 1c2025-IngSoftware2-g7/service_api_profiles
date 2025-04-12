from src.domain.profile import Profile
from werkzeug.security import generate_password_hash
from src.infrastructure.config.db_config import DatabaseConfig
from src.infrastructure.persistence.base_entity import BaseEntity


class ProfilesRepository(BaseEntity):
    def __init__(self, logger):
        self.log = logger
        super().__init__()  # Inicializa self.conn y self.cursor (heredado de BaseEntity)

    def _parse_profile(self, profile_data):
        """Convierte datos de la DB a objeto Profile (similar a _parse_user en UsersRepository)"""
        return Profile(
            uuid=profile_data["uuid"],
            name=profile_data["name"],
            surname=profile_data["surname"],
            email=profile_data["email"],
            password=profile_data["password"],
            role=profile_data["role"],
            location=profile_data.get("location"),  # Ahora es str
            profile_picture=profile_data.get("profile_picture")
        )

    def profile_exists(self, profile_uuid: str) -> bool:
        """Verifica si un perfil existe (similar a check_email en UsersRepository)"""
        query = "SELECT 1 FROM profiles WHERE uuid = %s LIMIT 1"
        params = (str(profile_uuid),)
        self.cursor.execute(query, params)
        return bool(self.cursor.fetchone())

    def insert_profile(self, profile_data: dict):
        """Inserta un perfil (similar a insert_user en UsersRepository)"""
        query = """
        INSERT INTO profiles (
            uuid, name, surname, email, password, role, location, profile_picture
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        # Hashear la contraseña
        profile_data["password"] = generate_password_hash(
            profile_data["password"])

        params = (
            profile_data["uuid"],
            profile_data["name"],
            profile_data["surname"],
            profile_data["email"],
            profile_data["password"],
            profile_data["role"],
            profile_data.get("location"),
            profile_data.get("profile_picture")
        )

        self.cursor.execute(query, params)
        self.conn.commit()
        return self._parse_profile(profile_data)

    def get_profile(self, uuid):
        """Obtiene un perfil por UUID (similar a get_user en UsersRepository)"""
        query = "SELECT * FROM profiles WHERE uuid = %s"
        params = (str(uuid),)
        self.cursor.execute(query, params)
        profile = self.cursor.fetchone()

        if not profile:
            return None

        # Mapear resultados a un diccionario (asumiendo que cursor.description existe)
        columns = [desc[0] for desc in self.cursor.description]
        profile_data = dict(zip(columns, profile))
        return self._parse_profile(profile_data)

    def update_profile(self, uuid, updates):
        # Construir la consulta dinámica
        set_clause = ", ".join([f"{field} = %s" for field in updates.keys()])
        query = f"""
            UPDATE profiles
            SET {set_clause}, updated_at = NOW()
            WHERE uuid = %s
            RETURNING *
        """

        params = list(updates.values()) + [uuid]

        self.cursor.execute(query, params)
        self.conn.commit()

        updated_profile = self.cursor.fetchone()
        if not updated_profile:
            raise ValueError("Profile not found after update")

        # Convertir a diccionario
        columns = [desc[0] for desc in self.cursor.description]
        profile_data = dict(zip(columns, updated_profile))

        return self._parse_profile(profile_data)
