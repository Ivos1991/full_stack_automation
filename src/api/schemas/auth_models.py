from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthCredentials:
    username: str
    password: str
    remember: bool | None = None


@dataclass(frozen=True)
class CurrentUser:
    id: str | int | None
    username: str
    first_name: str | None = None
    last_name: str | None = None
    balance: int | None = None
