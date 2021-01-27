"""

test telegram_bot.py
"""
import logging

import pytest

from rysolv_monitor.telegram_bot import (
    RysolvBot,
)

def test_init_bot(init_database):
    """

    test init_bot
    :param init_database:
    :return:
    """
    _token = ""
    _bot = RysolvBot(_token, init_database, logging.getLogger("test"))

@pytest.mark.parametrize("data, expected", [
    ("49e9f746-c265-447f-ae66-4fbbeb910ab0", set(["49e9f746-c265-447f-ae66-4fbbeb910ab0"])),
    ("https://rysolv.com/issues/detail/49e9f746-c265-447f-ae66-4fbbeb910ab0",
     set(["49e9f746-c265-447f-ae66-4fbbeb910ab0"])),
    ("https://rysolv.com/issues/detail/49e9f746-c265-447f-ae66-4fbbeb910ab0 & https://rysolv.com/issues/detail/9fdc5d5a-bcca-40a8-9e1e-b2a53860acd9",
     set(["49e9f746-c265-447f-ae66-4fbbeb910ab0", "9fdc5d5a-bcca-40a8-9e1e-b2a53860acd9"])),
    ("fezfez545zeg4", set()),
])
def test_find_all_uuid(data, expected):
    assert RysolvBot.find_all_uuid(data) == expected
