"""

types modules
"""
from .utils import (
    escape,
    url_from_issue
)


class Comment(dict):
    """

    Comment class
    """

class Issue(dict):
    """

    Issue class
    """

    def url_from_issue(self) -> str:
        """

        url from issue
        :return:
        """
        return url_from_issue(self["id"])

    def __str__(self):
        return f"*New {escape(self.get('type'))} from {escape(self.get('organizationName'))}*\n" \
               rf"Name\: {escape(self.get('name'))}" \
               rf"\- Language\: {escape(','.join(self.get('language')))}\n" \
               rf" Funded amount\: {self.get('fundedAmount')}$ \- {self.get('comments')} comments" \
               rf" \- {len(self['attempting'])} attemptings\n" \
               f"[Rysolv]({self.url_from_issue()})\n" \
               f"[Github]({self.get('repo')})\n" \
               rf"Last update\: {escape(str(self.get('modifiedDate')))}"
