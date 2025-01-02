from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.losca_City_Planning import LoscaCityPlanningSpider

test_response = file_response(
    join(dirname(__file__), "files", "losca_City_Planning.json"),
    url="https://planning.lacity.gov/dcpapi/meetings/api/all/commissions/2024",
)
spider = LoscaCityPlanningSpider()

freezer = freeze_time("2024-10-21")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Zoning Administration"


def test_description():
    assert parsed_items[0]["description"] == "South Valley ZA Hearing Agenda"


def test_start():
    assert parsed_items[0]["start"] == datetime(2025, 1, 30, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "losca_City_Planning/202501300000/x/zoning_administration"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "11649, 11649 1/2, 11651, 11651 1/2 West Riverside Drive",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://planning.lacity.gov/about/commissions-boards-hearings"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "http://planning.lacity.gov/dcpapi2/meetings/document/77987",
            "title": "Agenda",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == "Not classified"


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
