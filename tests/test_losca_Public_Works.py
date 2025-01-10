from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.losca_Public_Works import LoscaPublicWorksSpider

test_response = file_response(
    join(dirname(__file__), "files", "losca_Public_Works.json"),
    url=(
        "https://api.lacity.org/city_calendar?_format=json&display_id=rest_export&"
        "start=2024-07-06&eventtype=ENS%20-%20Meeting%20-%20Board&department=Board%20of"
        "%20Public%20Works&offset=0&items_per_page=15"
    ),
)
spider = LoscaPublicWorksSpider()

freezer = freeze_time("2025-01-06")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 15


def test_title():
    assert parsed_items[0]["title"] == "Board of Public Works Agenda"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 7, 10, 10, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "Please check meeting source for time and location details"
    )


def test_id():
    assert (
        parsed_items[0]["id"]
        == "losca_Public_Works/202407101000/x/board_of_public_works_agenda"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "City Hall",
        "address": "200 N Spring St, Los Angeles, CA 90012",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://calendar.lacity.org/node/331721"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": (
                "https://ens.lacity.org/bpw/agendas/bpwagendas86181574_07102024.pdf"
            ),
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
