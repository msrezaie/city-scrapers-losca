from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.losca_Housing_Authority import LoscaHousingAuthoritySpider

test_response = file_response(
    join(dirname(__file__), "files", "losca_Housing_Authority.html"),
    url="https://www.hacla.org/en/bocfiles",
)
spider = LoscaHousingAuthoritySpider()

freezer = freeze_time("2025-01-08")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 22

def test_title():
    assert parsed_items[0]["title"] == "BOC Regular Meeting"
    assert parsed_items[1]["title"] == "Board of Directors Special Meeting"
    assert parsed_items[20]["title"] == "BOC Regular Meeting"
    assert parsed_items[21]["title"] == "Board of Directors Special Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2025, 1, 9, 9, 0)
    assert parsed_items[21]["start"] == datetime(2024, 7, 11, 9, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert parsed_items[0]["id"] == "losca_Housing_Authority/202501090900/x/boc_regular_meeting"


def test_status():
    assert parsed_items[0]["status"] == "tentative"
    assert parsed_items[21]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "HACLA",
        "address": "2600 Wilshire Blvd. Los Angeles, CA 90057"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.hacla.org/en/bocfiles"


def test_links():
    assert parsed_items[0]["links"] == []
    assert parsed_items[3]["links"] == [{
        'title': 'Audio',
        'href': 'https://hacla.org/sites/default/files/2024-12/Audio- 12.12.24 BOC Regular Meeting.mp4',
    }]
    assert parsed_items[9]["links"] == [
        {
            'title': 'Minutes',
            'href': 'https://hacla.org/sites/default/files/2024-11/2024.11.14 Action Minutes--BOC Regular Meeting.pdf',
        },
        {
            'title': 'Audio',
            'href': 'https://hacla.org/sites/default/files/2024-11/Audio- 11.14.2024 BOC, BHI Regular Meeting.mp4',
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
