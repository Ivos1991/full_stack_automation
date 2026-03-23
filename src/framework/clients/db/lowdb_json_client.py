from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from typing import Any

from src.framework.clients.db.base_db_client import BaseDBClient
from src.framework.logging.logger import get_logger
from src.framework.reporting.allure_helpers import attach_json

LOWDB_WRITE_LOCK = RLock()


class LowDBJSONClient(BaseDBClient):
    def __init__(self, data_file: str) -> None:
        super().__init__(host="", port=0, database=data_file, user="", password="")
        self.data_file = Path(data_file)
        self.logger = get_logger(self.__class__.__name__)

    def connect(self) -> dict[str, Any]:
        self.connection = self.read_state()
        self.logger.info("Loaded RWA lowdb data from %s", self.data_file)
        return self.connection

    def execute(self, query: Any, parameters: tuple[Any, ...] | None = None) -> Any:
        raise NotImplementedError("LowDBJSONClient does not support arbitrary execute operations.")

    def fetch_one(self, query: dict[str, str], parameters: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
        if not parameters:
            return None

        data = self.read_state()
        entity_name = query["entity"]
        lookup_field = query["lookup_field"]
        lookup_value = parameters[0]

        for item in data.get(entity_name, []):
            if item.get(lookup_field) == lookup_value:
                attach_json(
                    name=f"{self.__class__.__name__}-fetch-one",
                    content={"query": query, "parameters": parameters, "result": item},
                )
                return item
        attach_json(
            name=f"{self.__class__.__name__}-fetch-one",
            content={"query": query, "parameters": parameters, "result": None},
        )
        return None

    def read_state(self) -> dict[str, Any]:
        if not self.data_file.exists():
            raise FileNotFoundError(f"RWA data file was not found: {self.data_file}")

        return json.loads(self.data_file.read_text(encoding="utf-8"))

    def write_state(self, state: dict[str, Any]) -> None:
        """Persist lowdb state atomically so concurrent repository tests do not leave partial writes behind."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        with LOWDB_WRITE_LOCK:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_file.parent,
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                json.dump(state, temporary_file, indent=2)
                temporary_file.write("\n")
                temporary_path = Path(temporary_file.name)

            temporary_path.replace(self.data_file)
            self.connection = state

    def mutate_state(self, mutator) -> Any:
        """Lock, load, mutate, and persist lowdb state as one repository-level operation."""
        with LOWDB_WRITE_LOCK:
            state = self.read_state()
            result = mutator(state)
            self.write_state(state)
            return result
