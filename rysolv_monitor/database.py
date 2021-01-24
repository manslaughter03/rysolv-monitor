"""

database module
"""
from enum import Enum, auto
import os
from typing import Dict, List
import json
import time

from pymongo import DESCENDING
from pymongo.results import UpdateResult, DeleteResult
from pymongo.database import Database
from pymongo.errors import CollectionInvalid

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")


class RysolvCollections(Enum):
    """

    RysolvCollections class
    """
    Users = auto()
    WatchIssues = auto()

def _load_schema_file(collection_name: str) -> Dict:
    _file_path = os.path.join(SCHEMA_DIR, f"{collection_name}.json")
    with open(_file_path, "r") as _file:
        return json.load(_file)


class RysolvDatabase:
    """

    RysolvDatabase class
    """
    SCHEMAS = {
        RysolvCollections.Users.name: _load_schema_file(RysolvCollections.Users.name),
        RysolvCollections.WatchIssues.name: _load_schema_file(RysolvCollections.WatchIssues.name),
    }
    def __init__(self, database: Database):
        self.database = database
        self.collections = {}
        self._init_collections()

    def _init_collections(self):
        for collection_name in RysolvCollections.__members__.keys():
            try:
                self.database.create_collection(collection_name)
                if collection_name == RysolvCollections.Users.name:
                    self.database[collection_name].create_index([("user_id", DESCENDING)],
                                                                unique=True)
                if collection_name == RysolvCollections.WatchIssues.name:
                    self.database[collection_name].create_index([("user_id", DESCENDING),
                                                                 ("issue_id", DESCENDING)],
                                                                unique=True)
            except CollectionInvalid:
                pass
            self.collections[collection_name] = self.database[collection_name]

    def find_users(self) -> List[Dict]:
        """

        find users
        :return:
        """
        return self.collections[RysolvCollections.Users.name].find({})

    def update_user(self, user_id: int) -> UpdateResult:
        """

        update user
        :param user_id:
        :return:
        """
        _filter = {"user_id": user_id}
        _data = {"user_id": user_id, "last_update": time.time()}
        return self.collections[RysolvCollections.Users.name].update_one(_filter,
                                                                                  {"$set": _data},
                                                                                  upsert=True)

    def delete_user(self, user_id: int) -> DeleteResult:
        """

        delete user by user_id
        :param user_id:
        :return:
        """
        _filter = {"user_id": user_id}
        return self.collections[RysolvCollections.Users.name].delete_one(_filter)

    def update_watch_issue(self, user_id: int, issue_id: str) -> UpdateResult:
        """

        update watch issue
        :param user_id:
        :param issue_id:
        :return:
        """
        _filter = {"user_id": user_id, "issue_id": issue_id}
        _data = {"user_id": user_id, "issue_id": issue_id, "last_update": time.time()}
        return self.collections[RysolvCollections.WatchIssues.name].update_one(_filter,
                                                                               {"$set": _data},
                                                                               upsert=True)

    def delete_watch_issue(self, user_id: int, issue_id: str) -> DeleteResult:
        """

        delete watch issue
        :param user_id:
        :param issue_id:
        :return:
        """
        _filter = {"user_id": user_id, "issue_id": issue_id}
        return self.collections[RysolvCollections.WatchIssues.name].delete_one(_filter)

    def find_watch_issues(self) -> List[Dict]:
        """

        find watch issue
        :return:
        """
        return self.collections[RysolvCollections.WatchIssues.name].find({})

    def clear(self) -> None:
        """

        clear database
        :return:
        """
        for collection_name in RysolvCollections.__members__.keys():
            self.database.drop_collection(collection_name)
