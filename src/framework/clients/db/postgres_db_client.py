from __future__ import annotations

from typing import Any

from src.framework.clients.db.base_db_client import BaseDBClient
from src.framework.logging.logger import get_logger


class PostgresDBClient(BaseDBClient):
    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        super().__init__(host=host, port=port, database=database, user=user, password=password)
        self.logger = get_logger(self.__class__.__name__)

    def connect(self) -> Any:
        if self.connection is not None:
            return self.connection

        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as error:  # pragma: no cover - depends on local environment
            raise RuntimeError("psycopg is required for PostgreSQL integration.") from error

        self.connection = psycopg.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password,
            row_factory=dict_row,
        )
        self.logger.info("Connected to PostgreSQL at %s:%s/%s", self.host, self.port, self.database)
        return self.connection

    def execute(self, query: str, parameters: tuple[Any, ...] | None = None) -> Any:
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or ())
            return cursor

    def fetch_one(self, query: str, parameters: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        connection = self.connect()
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or ())
            row = cursor.fetchone()
        return row
