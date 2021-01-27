from pymongo import MongoClient
import pytest

from rysolv_monitor.database import RysolvDatabase


@pytest.fixture
def init_database():
    """

    init database fixture
    """
    _db_url = "mongodb://127.0.0.1:27017"
    _db_name = "rysolv_test"
    _db_client = MongoClient(_db_url)
    _pymongo_database = RysolvDatabase(_db_client[_db_name])
    yield _pymongo_database
    _pymongo_database.clear()
