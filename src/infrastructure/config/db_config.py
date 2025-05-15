import os

from src.logger_config import get_logger

logger = get_logger("api-profiles")

class DatabaseConfig:
    host: str
    database: str
    user: str
    password: str

    """
    Order of precedence of variables:
    - Production: This uses the cloud deployment environment variables. 
    - Local: This uses local variables (.env).
    """

    def __init__(self):
        self.database = os.environ.get("DB_NAME")
        self.user = os.environ.get("DB_USER")
        self.host = os.environ.get("DB_HOST")
        self.password = os.environ.get("DB_PASSWORD")
        self.port = os.environ.get("DB_PORT")

    @property
    def connection_strings(self) -> str:
        connection_strings = f"dbname={self.database} user={self.user} host={self.host} password={self.password} port={self.port}"
        logger.debug(f"Profile API - connection_strings: {connection_strings}")
        return connection_strings
