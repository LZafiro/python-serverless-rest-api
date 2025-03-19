from contextlib import contextmanager
from typing import Generator, Dict, Any, List, Optional
import logging

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

from src.config.db_config import DBConfig, get_db_config
from src.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _pool = None

    def __new__(cls, config: Optional[DBConfig] = None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize(config or get_db_config())
        return cls._instance

    def _initialize(self, config: DBConfig) -> None:
        self.config = config
        try:
            self._pool = ThreadedConnectionPool(
                minconn=config.min_connections,
                maxconn=config.max_connections,
                dsn=config.connection_string,
                connect_timeout=config.connection_timeout,
                options=f'-c statement_timeout={config.connection_timeout * 1000}'
            )
            logger.info(f"Initialized database connection pool to {config.host}:{config.port}/{config.name}")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {str(e)}")
            raise DatabaseError(f"Database connection failed: {str(e)}")

    @contextmanager
    def connection(self) -> Generator:
        conn = None
        try:
            assert self._pool is not None
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        finally:
            if conn:
                assert self._pool is not None
                self._pool.putconn(conn)

    @contextmanager
    def cursor(self, cursor_factory=RealDictCursor) -> Generator:
        with self.connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute(self, query: str, params: Dict[str, Any] = {}) -> None:
        with self.cursor() as cursor:
            cursor.execute(query, params or {})

    def fetch_one(self, query: str, params: Dict[str, Any] = {}) -> Optional[Dict[str, Any]]:
        with self.cursor() as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchone()

    def fetch_all(self, query: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        with self.cursor() as cursor:
            cursor.execute(query, params or {})
            return cursor.fetchall()

    def close(self) -> None:
        if self._pool:
            self._pool.closeall()
            logger.info("Closed database connection pool")
