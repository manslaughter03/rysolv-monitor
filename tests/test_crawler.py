"""

test crawler.py
"""
import logging

from rysolv_monitor.crawler import RysolvCrawler

def test_monitor_issue(init_database):
    """

    test monitor_issue
    :param init_database:
    :return:
    """
    crawler = RysolvCrawler(init_database, logging.getLogger("test"))
    data = crawler._monitor_issue()
    assert data

def test_fetch_issues():
    """

    test fetch
    :return:
    """
    crawler = RysolvCrawler(init_database, logging.getLogger("test"))
    data = crawler.fetch_issues()
    assert data

def test_fetch_comments_by_issue_id(init_database):
    """

    test fetch
    :return:
    """
    crawler = RysolvCrawler(init_database, logging.getLogger("test"))
    _issue_id = "06684c3a-8a70-4e4c-a92e-c74b661b3390"
    data = crawler.fetch_comments_by_issue_id(_issue_id)
    assert data


def test_convert_to_datetime():
    """

    test convert to datetime
    :return:
    """
    _date_convert = RysolvCrawler.convert_to_datetime("2020-12-23T18:00:00.417Z")
    assert str(_date_convert) == "2020-12-23 18:00:00.417000"
