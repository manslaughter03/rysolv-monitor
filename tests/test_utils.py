import os

from rysolv_monitor.utils import parse_changelog


def test_parse_changelog():
    filepath = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")
    data = parse_changelog(filepath)
    assert data
