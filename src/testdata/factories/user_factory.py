from __future__ import annotations

from uuid import uuid4

from src.api.schemas.user_models import GeneratedUserData


class UserFactory:
    def build_rwa_user(self) -> GeneratedUserData:
        user_suffix = uuid4().hex[:8]
        numeric_suffix = "".join(str(int(character, 16) % 10) for character in user_suffix)[:10]

        return GeneratedUserData(
            first_name="Test",
            last_name=f"User{user_suffix[:4]}",
            username=f"rwa_user_{user_suffix}",
            password=f"Rwa-{user_suffix}!",
            email=f"rwa_user_{user_suffix}@example.test",
            phone_number=f"555-{numeric_suffix[:3]}-{numeric_suffix[3:7]}",
            balance=0,
            avatar=f"https://api.dicebear.com/7.x/identicon/svg?seed={user_suffix}",
            default_privacy_level="public",
        )
