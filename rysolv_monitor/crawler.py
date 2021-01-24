"""

crawler module
"""
from typing import List
from queue import Queue
import time
from datetime import datetime

import requests

from .types import (
    Issue
)
from .constant import BASE_URL


class RysolvCrawler:
    """

    RysolvCrawler class
    """
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __init__(self, queue: Queue, sleep_time: int = 5):
        self.queue = queue
        self.sleep_time = sleep_time

    def run(self) -> None:
        """

        run function
        :return:
        """
        self._monitor_issue()

    def _monitor_issue(self):
        while True:
            _data = self.fetch()
            self.queue.put(_data)
            time.sleep(self.sleep_time)

    def fetch(self) -> List[Issue]:
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
        _data = {"query": _query}
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

        _result_data = resp.json()
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

    @classmethod
    def convert_to_datetime(cls, date_str: str) -> datetime:
        """

        convert to datetime
        :param date_str:
        :return:
        """
        return datetime.strptime(date_str, cls.DATE_FORMAT)
