"""

utils module
"""

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
