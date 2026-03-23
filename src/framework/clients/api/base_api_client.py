from __future__ import annotations

from typing import Any

import requests

from src.framework.logging.logger import get_logger
from src.framework.reporting.allure_helpers import attach_json


class BaseAPIClient:
    def __init__(self, base_url: str, session: requests.Session | None = None, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.timeout = timeout
        self.logger = get_logger(self.__class__.__name__)

    def build_url(self, path: str) -> str:
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{self.base_url}{normalized_path}"

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = self.build_url(path)
        payload = kwargs.get("json")
        response = self.session.request(method=method.upper(), url=url, timeout=self.timeout, **kwargs)
        self.logger.info("%s %s -> %s", method.upper(), url, response.status_code)
        if payload is not None:
            attach_json(name=f"{self.__class__.__name__}-{method.lower()}-request", content=payload)
        attach_json(
            name=f"{self.__class__.__name__}-{method.lower()}-response",
            content={"url": url, "status_code": response.status_code},
        )
        return response

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> requests.Response:
        return self.request("PATCH", path, **kwargs)
