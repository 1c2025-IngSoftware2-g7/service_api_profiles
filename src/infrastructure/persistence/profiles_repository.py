from src.domain.profile import Profile
from werkzeug.security import generate_password_hash
from src.infrastructure.config.db_config import DatabaseConfig
from src.infrastructure.persistence.base_entity import BaseEntity


class ProfilesRepository(BaseEntity):
    def __init__(self, logger):
        self.log = logger
        super().__init__()

    def _parse_profile(self, profile_data):
        """Convierte datos de la DB a objeto Profile"""
        return Profile(
            uuid=profile_data["uuid"],
            email=profile_data["email"],
            role=profile_data["role"],
            display_name=profile_data["display_name"],
            phone=profile_data["phone"],
            location=profile_data["location"],
            birthday=profile_data["birthday"],
            gender=profile_data["gender"],
            description=profile_data["description"],
            display_image=profile_data["display_image"],
        )

    def profile_exists(self, profile_uuid: str) -> bool:
        """Verifica si un perfil existe"""
        query = "SELECT 1 FROM profiles WHERE uuid = %s LIMIT 1"
        params = (str(profile_uuid),)
        self.cursor.execute(query, params)
        return bool(self.cursor.fetchone())

    def insert_profile(self, profile_data: dict):
        """Inserta un nuevo perfil con campos obligatorios y opcionales"""
        query = """
        INSERT INTO profiles (
            uuid, email, role, display_name, location, 
            birthday, gender, description, display_image, phone
        ) VALUES (
            %(uuid)s, %(email)s, %(role)s, %(display_name)s, %(location)s,
            %(birthday)s, %(gender)s, %(description)s, %(display_image)s, %(phone)s
        )
        RETURNING *
        """

        # Validar campos obligatorios
        required_fields = ["uuid", "email", "role"]
        missing_fields = [
            field for field in required_fields if field not in profile_data
        ]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Establecer valores por defecto como NULL para campos opcionales no proporcionados
        optional_fields = [
            "display_name",
            "location",
            "birthday",
            "gender",
            "description",
            "display_image",
            "phone",
        ]
        for field in optional_fields:
            if field not in profile_data:
                profile_data[field] = None

        self.cursor.execute(query, profile_data)
        self.conn.commit()

        # Obtener y retornar el perfil creado
        new_profile = self.cursor.fetchone()
        columns = [desc[0] for desc in self.cursor.description]
        return self._parse_profile(dict(zip(columns, new_profile)))

    def get_profile(self, uuid):
        """Obtiene un perfil por UUID"""
        query = "SELECT * FROM profiles WHERE uuid = %s"
        params = (str(uuid),)
        self.cursor.execute(query, params)
        profile = self.cursor.fetchone()

        if not profile:
            return None

        # Mapear resultados a un diccionario
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
