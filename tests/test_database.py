import pytest

from rysolv_monitor.database import RysolvCollections


def test_database_init_collections(init_database):
    assert init_database.collections

@pytest.mark.parametrize("data", [
    ({"user_id": 55555}),
    pytest.param({"user_id": "aa"}, marks=pytest.mark.xfail),
])
def test_database_users_validator(init_database, data):
    init_database.collections[RysolvCollections.Users.name].insert_one(data)

@pytest.mark.parametrize("data", [
    ({"user_id": 55555, "issue_id": 495959}),
    pytest.param({"user_id": 555}, marks=pytest.mark.xfail),
    pytest.param({"isssue_id": 555}, marks=pytest.mark.xfail),
    pytest.param({"user_id": 55555, "issue_id": "495959"}, marks=pytest.mark.xfail),
    pytest.param({"user_id": "55555", "issue_id": 495959}, marks=pytest.mark.xfail),
])
def test_database_watch_issue_validator(init_database, data):
    init_database.collections[RysolvCollections.WatchIssues.name].insert_one(data)

def test_database_find_last_version(init_database):
    version = init_database.find_last_version()
    assert not version
