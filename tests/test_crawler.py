from rysolv_monitor import RysolvCrawler

def test_fetch():
    crawler = RysolvCrawler()
    data = crawler.fetch()
    assert data


def test_convert_to_datetime():
    _date_convert = RysolvCrawler.convert_to_datetime("2020-12-23T18:00:00.417Z")
    assert str(_date_convert) == "2020-12-23 18:00:00.417000"
