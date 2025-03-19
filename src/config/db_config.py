import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

@dataclass
class DBConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    min_connections: int = 1
    max_connections: int = 10
    connection_timeout: int = 30
    idle_timeout: int = 300

    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@lru_cache()
def get_db_config() -> DBConfig:
    return DBConfig(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        name=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        min_connections=int(os.environ.get("DB_MIN_CONNECTIONS", "1")),
        max_connections=int(os.environ.get("DB_MAX_CONNECTIONS", "10")),
        connection_timeout=int(os.environ.get("DB_CONNECTION_TIMEOUT", "30")),
        idle_timeout=int(os.environ.get("DB_IDLE_TIMEOUT", "300")),
    )
