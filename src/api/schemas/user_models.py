from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UserSummary:
    id: str | int | None
    username: str


@dataclass(frozen=True)
class GeneratedUserData:
    first_name: str
    last_name: str
    username: str
    password: str
    email: str
    phone_number: str
    balance: int
    avatar: str
    default_privacy_level: str = "public"

    def to_api_payload(self) -> dict[str, Any]:
        return {
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "phoneNumber": self.phone_number,
            "balance": self.balance,
            "avatar": self.avatar,
            "defaultPrivacyLevel": self.default_privacy_level,
        }


@dataclass(frozen=True)
class CreatedUser:
    id: str
    username: str
    first_name: str
    last_name: str
    email: str | None = None
