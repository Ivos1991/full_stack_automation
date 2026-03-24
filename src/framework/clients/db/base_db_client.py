from __future__ import annotations
from typing import Any

class BaseDBClient:
    def __init__(self, host: str, port: int, database: str, user: str, password: str) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection: Any | None = None

    def connect(self) -> Any:
        raise NotImplementedError

    def close(self) -> None:
        if self.connection and hasattr(self.connection, "close"):
            self.connection.close()
        self.connection = None

    def fetch_one(self, query: Any, parameters: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        raise NotImplementedError

    def execute(self, query: Any, parameters: tuple[Any, ...] | None = None) -> Any:
        raise NotImplementedError

    def read_state(self) -> dict[str, Any]:
        raise NotImplementedError

    def write_state(self, state: dict[str, Any]) -> None:
        raise NotImplementedError

    def mutate_state(self, mutator) -> Any:
        raise NotImplementedError
