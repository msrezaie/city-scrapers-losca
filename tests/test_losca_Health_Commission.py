from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.losca_Health_Commission import LoscaHealthCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "losca_Health_Commission.json"),
    url="https://clerk.lacity.gov/clerk-services/council-and-public-services/city-health-commission/commission-meetings",  # noqa
)
spider = LoscaHealthCommissionSpider()

freezer = freeze_time("2024-10-22")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_items[0]["title"] == "Los Angeles City Health Commission"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 1, 8, 18, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "losca_Health_Commission/202401081800/x/los_angeles_city_health_commission"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Los Angeles City Health Commission",
        "address": "Room 340 (CITY HALL), 200 N Spring St, Los Angeles, CA 90012",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://clerk.lacity.gov/clerk-services/council-and-public-services/city-health-commission/commission-meetings"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {"href": "https://youtube.com/watch?v=aWd67e6sxTg", "title": "Video Link"},
        {
            "href": "https://lacity.primegov.com/Portal/Meeting?meetingTemplateId=124727",  # noqa
            "title": "HTML Agenda",
        },
        {
            "href": "https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId=124727&compileOutputType=1",  # noqa
            "title": "Agenda",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
