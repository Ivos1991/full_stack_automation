from __future__ import annotations

from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from assertpy import assert_that
import pytest

from src.db.repositories.users_repository import UsersRepository
from src.framework.clients.db.lowdb_json_client import LowDBJSONClient
from src.framework.config.settings import get_settings


@pytest.mark.db
class TestUsersRepository:
    def test_created_user_is_persisted_in_lowdb(self, require_live_rwa_environment, created_user, connected_users_repository):
        persisted_user = connected_users_repository.get_user_by_username(created_user.username)

        assert_that(persisted_user, "Expected created user in lowdb").is_not_none()
        assert_that(persisted_user["id"], "Expected persisted user id").is_equal_to(created_user.id)
        assert_that(persisted_user["username"], "Expected persisted username").is_equal_to(created_user.username)

    def test_repository_can_create_and_delete_user_in_isolated_lowdb_copy(self, generated_user_data):
        source_path = get_settings().rwa_data_file
        if not source_path:
            pytest.skip("RWA_DATA_FILE is not configured for isolated lowdb-copy repository validation.")

        source_file = Path(source_path)
        if not source_file.is_file():
            pytest.skip(f"RWA lowdb file is not available for isolated repository validation: {source_file}")

        local_temp_root = Path.cwd() / "artifacts" / "tmp"
        try:
            local_temp_root.mkdir(parents=True, exist_ok=True)

            with TemporaryDirectory(dir=local_temp_root) as temp_dir:
                temporary_data_file = Path(temp_dir) / "database.json"
                shutil.copyfile(source_file, temporary_data_file)

                db_client = LowDBJSONClient(data_file=str(temporary_data_file))
                users_repository = UsersRepository(db_client=db_client)

                created_user = users_repository.create_user(generated_user_data)
                persisted_user = users_repository.get_user_by_username(generated_user_data.username)
                users_repository.delete_user_and_related_data(created_user["id"])
                deleted_user = users_repository.get_user_by_username(generated_user_data.username)

                assert_that(created_user["username"], "Expected created repository username").is_equal_to(
                    generated_user_data.username
                )
                assert_that(persisted_user, "Expected repository-created user").is_not_none()
                assert_that(deleted_user, "Expected deleted repository user").is_none()
        except PermissionError as error:
            pytest.skip(f"Local filesystem permissions do not allow isolated lowdb-copy validation: {error}")
