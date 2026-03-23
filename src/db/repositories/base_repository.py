from __future__ import annotations

from src.framework.clients.db.base_db_client import BaseDBClient


class BaseRepository:
    def __init__(self, db_client: BaseDBClient) -> None:
        self.db_client = db_client

