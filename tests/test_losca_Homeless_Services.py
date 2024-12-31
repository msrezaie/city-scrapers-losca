from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import (
    BOARD,
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
)
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.losca_Homeless_Services import LoscaHomelessServicesSpider

test_response = file_response(
    join(dirname(__file__), "files", "losca_Homeless_Services.html"),
    url="https://www.lahsa.org/events",
)
spider = LoscaHomelessServicesSpider()

freezer = freeze_time("2024-12-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 15


def test_title():
    assert parsed_items[0]["title"] == "CES Policy Council Meeting - Canceled"
    assert parsed_items[1]["title"] == "LA COC BOARD HMIS COMMITTEE MEETING"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 12, 25, 0, 0)
    assert parsed_items[1]["start"] == datetime(2025, 1, 8, 0, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == "Start time in Event Link"


def test_id():
    assert parsed_items[0]["id"] == "losca_Homeless_Services/202412250000/x/ces_policy_council_meeting"  # noqa


def test_status():
    assert parsed_items[0]["status"] == "cancelled"
    assert parsed_items[1]["status"] == "tentative"


def test_location():
    # if committee or commission or board
    #   LAHSA, 707 Wilshire Blvd, 10th Floor, Los Angeles, CA 90017
    # if council
    #   637 Wilshire Blvd, 1st Floor Commission Room, Los Angeles, CA 90017
    # city council is the only agency that doesn't meet at usual LAHSA location
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[0]["location"] == {
        "name": "City Council (check Event Link)",
        "address": "637 Wilshire Blvd, 1st Floor Commission Room, Los Angeles, CA 90017"
    }
    # board uses default location
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[1]["location"] == {
        "name": "LAHSA (check Event Link)",
        "address": "707 Wilshire Blvd, 10th Floor, Los Angeles, CA 90017"
    }
    # committee uses default location
    assert parsed_items[3]["classification"] == COMMITTEE
    assert parsed_items[3]["location"] == {
        "name": "LAHSA (check Event Link)",
        "address": "707 Wilshire Blvd, 10th Floor, Los Angeles, CA 90017"
    }
    # commission uses default location
    assert parsed_items[5]["classification"] == COMMISSION
    assert parsed_items[5]["location"] == {
        "name": "LAHSA (check Event Link)",
        "address": "707 Wilshire Blvd, 10th Floor, Los Angeles, CA 90017"
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.lahsa.org/events"


def test_links():
    assert parsed_items[0]["links"] == [{
        "title": "Event Link",
        "href": "https://www.lahsa.org/events?e=1412-ces-policy-council-meeting-canceled"  # noqa
    }]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[1]["classification"] == BOARD
    assert parsed_items[2]["classification"] == BOARD
    assert parsed_items[3]["classification"] == COMMITTEE
    assert parsed_items[4]["classification"] == COMMITTEE
    assert parsed_items[5]["classification"] == COMMISSION
    assert parsed_items[6]["classification"] == CITY_COUNCIL
    assert parsed_items[7]["classification"] == COMMITTEE
    assert parsed_items[8]["classification"] == COMMITTEE
    assert parsed_items[9]["classification"] == CITY_COUNCIL
    assert parsed_items[10]["classification"] == COMMISSION
    assert parsed_items[11]["classification"] == COMMITTEE
    assert parsed_items[12]["classification"] == COMMITTEE
    assert parsed_items[13]["classification"] == CITY_COUNCIL
    assert parsed_items[14]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
