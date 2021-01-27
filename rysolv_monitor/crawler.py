"""

crawler module
"""
from typing import List, Dict
from logging import Logger
import time
from datetime import datetime

import requests

from .types import (
    Issue,
    Comment
)
from .constant import BASE_URL
from .database import RysolvDatabase


class RysolvCrawler:
    """

    RysolvCrawler class
    """
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self,
                 database: RysolvDatabase,
                 logger: Logger,
                 sleep_time: int = 5):
        self.database = database
        self.sleep_time = sleep_time
        self.logger = logger

    def run(self) -> None:
        """

        run function
        :return:
        """
        self.logger.info("Run monitor issue")
        self._monitor_issue()

    def _monitor_issue(self):
        while True:
            _data = self.fetch_issues()
            self.logger.info("Find %s issues", len(_data))
            _result = self.database.write_issues(_data)
            self.logger.debug("Update issues collections %d modified %d upserted",
                              _result.modified_count,
                              _result.upserted_count)
            _comments = []
            for _issue in _data:
                _comments.append({"issue_id": _issue["id"],
                                  "comments": self.fetch_comments_by_issue_id(_issue["id"])})
            if _comments:
                _result = self.database.write_comments(_comments)
                self.logger.debug("Update comments collections %d modified %d upserted",
                                  _result.modified_count,
                                  _result.upserted_count)
            self.logger.info("Sleep %ds", self.sleep_time)
            time.sleep(self.sleep_time)

    def fetch_comments_by_issue_id(self, issue_id: str) -> List[Comment]:
        """

        fetch comments by issue id
        :param issue_id:
        :return:
        """
        _query = """
    query {{
      getIssueComments(issueId: \"{issue_id}\") {{
        body
        createdDate
        githubUrl
        isGithubComment
        profilePic
        userId
        username
      }}
    }}
    """.format(issue_id=issue_id)
        _result_data = self._query(_query)
        if "data" not in _result_data or \
                "getIssueComments" not in _result_data["data"]:
            raise Exception(f"Can't find data in response body: {_result_data}")
        return _result_data["data"]["getIssueComments"]

    def fetch_issues(self) -> List[Issue]:
        """

        fetch function
        :return:
        """
        _query = """
    query {
      getIssues {
        __typename
        ... on IssueArray {
          issues {
            attempting
            body
            comments
            createdDate
            fundedAmount
            id
            language
            modifiedDate
            name
            open
            organizationId
            organizationName
            organizationVerified
            rep
            repo
            type
            watching
          }
        }
        ... on Error {
          message
        }
      }
    }
  """
        _result_data = self._query(_query)
        if "data" not in _result_data or \
            "getIssues" not in _result_data["data"] or \
            "issues" not in _result_data["data"]["getIssues"]:
            raise Exception(f"Can't find data in response body: {_result_data}")
        _issues = []
        for item in _result_data["data"]["getIssues"]["issues"]:
            item["createdDate"] = self.convert_to_datetime(item["createdDate"])
            item["modifiedDate"] = self.convert_to_datetime(item["modifiedDate"])
            _issues.append(Issue(item))
        return _issues

    @staticmethod
    def _query(query: str) -> Dict:
        _data = {"query": query}
        _headers = {
            "content-type": "application/json",
            "user-agent": """Mozilla/5.0 (X11; Linux x86_64) """
                          """AppleWebKit/537.36 (KHTML, like Gecko) """
                          """Chrome/87.0.4280.141 Safari/537.36""",
        }
        resp = requests.post(f"{BASE_URL}/graphql", json=_data, headers=_headers)
        if not resp.status_code == 200:
            msg = f"Fail to query on {BASE_URL}, got {resp.status_code}" \
                  f"instead of 200, reason: {resp.reason}"
            raise Exception(msg)

        return resp.json()

    @classmethod
    def convert_to_datetime(cls, date_str: str) -> datetime:
        """

        convert to datetime
        :param date_str:
        :return:
        """
        return datetime.strptime(date_str, cls.DATE_FORMAT)
