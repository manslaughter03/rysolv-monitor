"""

utils module
"""
from typing import Dict
import re

from .constant import BASE_URL

def escape(text: str) -> str:
    """

    special escape for telegram message
    :param text:
    :return:
    """
    return text.replace("-", r"\-") \
            .replace("(", r"\(") \
            .replace(")", r"\)") \
            .replace("!", r"\!") \
            .replace(".", r"\.") \
            .replace("+", r"\+") \
            .replace("=", r"\=") \
            .replace("_", r"\_")


def url_from_issue(_id: str) -> str:
    """

    url from issue
    :param _id:
    :return:
    """
    return f"{BASE_URL}/issues/detail/{_id}"


def parse_changelog(filepath: str) -> Dict:
    """

    parse change log
    :param filepath:
    :return:
    """
    data = {}
    current_version = None
    with open(filepath, "r") as _file:
        _line = _file.readline()
        while _line:
            if _line.startswith("##"):
                _result = re.search("## ([0-9]+.[0-9]+.[0-9]+)", _line)
                if _result:
                    current_version = _result.group(1)
                    data[current_version] = ""
            elif current_version and _line != "\n":
                data[current_version] += _line
            _line = _file.readline()
    return data
