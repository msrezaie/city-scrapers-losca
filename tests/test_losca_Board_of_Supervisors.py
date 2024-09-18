from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.losca_Board_of_Supervisors import (
    LoscaBoardOfSupervisorsSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "losca_Board_of_Supervisors.html"),
    url="https://bos.lacounty.gov/board-meeting-agendas/",
)
spider = LoscaBoardOfSupervisorsSpider()

freezer = freeze_time("2024-09-17")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 10


def test_title():
    assert parsed_items[0]["title"] == "Policy Presentations and Public Hearing Meeting"
    assert parsed_items[1]["title"] == "Regular Board Meeting"
    assert parsed_items[2]["title"] == "Public Hearing Meeting"
    assert parsed_items[3]["title"] == "Regular Board Meeting"
    assert parsed_items[4]["title"] == "Policy Presentations Meeting"
    assert parsed_items[5]["title"] == "Regular Board Meeting"
    assert parsed_items[6]["title"] == "Regular Board Meeting"
    assert parsed_items[7]["title"] == "Regular Board Meeting"
    assert parsed_items[8]["title"] == "Budget Deliberations Board Meeting"
    assert parsed_items[9]["title"] == "Policy Presentations Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 9, 17, 9, 30)
    assert parsed_items[1]["start"] == datetime(2024, 9, 10, 9, 30)
    assert parsed_items[2]["start"] == datetime(2024, 8, 13, 11, 0)  # not 930am
    assert parsed_items[3]["start"] == datetime(2024, 8, 6, 9, 30)
    assert parsed_items[4]["start"] == datetime(2024, 7, 30, 9, 30)
    assert parsed_items[5]["start"] == datetime(2024, 7, 23, 9, 30)
    assert parsed_items[6]["start"] == datetime(2024, 7, 9, 9, 30)
    assert parsed_items[7]["start"] == datetime(2024, 6, 25, 9, 30)
    assert parsed_items[8]["start"] == datetime(2024, 6, 24, 9, 30)
    assert parsed_items[9]["start"] == datetime(2024, 6, 18, 9, 30)


def test_end():
    assert parsed_items[0]["end"] is None


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""


def test_id():
    assert (
        parsed_items[0]["id"]
        == "losca_Board_of_Supervisors/202409170930/x/policy_presentations_and_public_hearing_meeting"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"
    assert parsed_items[1]["status"] == "passed"
    assert parsed_items[2]["status"] == "passed"
    assert parsed_items[3]["status"] == "passed"
    assert parsed_items[4]["status"] == "passed"
    assert parsed_items[5]["status"] == "passed"
    assert parsed_items[6]["status"] == "passed"
    assert parsed_items[7]["status"] == "passed"
    assert parsed_items[8]["status"] == "passed"
    assert parsed_items[9]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Kenneth Hahn Hall of Administration",
        "address": "500 West Temple Street, Room 381B, Los Angeles",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://bos.lacounty.gov/board-meeting-agendas/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://assets-us-01.kc-usercontent.com/0234f496-d2b7-00b6-17a4-b43e949b70a2/522b6a97-181f-4a4d-a472-798ee3c7fc75/091724%20Agenda.htm",  # noqa
        },
        {
            "title": "PDF",
            "href": "https://assets-us-01.kc-usercontent.com:443/0234f496-d2b7-00b6-17a4-b43e949b70a2/d2b9d6cf-737c-4128-a54f-f1384fb4992e/Agenda_091724_links.pdf",  # noqa
        },
    ]
    assert parsed_items[1]["links"] == [
        {
            "title": "Agenda",
            "href": "https://assets-us-01.kc-usercontent.com/0234f496-d2b7-00b6-17a4-b43e949b70a2/2493f102-41f1-4483-9b65-39329b13e7a8/091024%20Agenda.htm",  # noqa
        },
        {
            "title": "PDF",
            "href": "https://assets-us-01.kc-usercontent.com:443/0234f496-d2b7-00b6-17a4-b43e949b70a2/d2af8220-c0e3-4d89-8370-c376023e1caf/Agenda_091024_links.pdf",  # noqa
        },
        {
            "title": "Supplemental",
            "href": "https://assets-us-01.kc-usercontent.com/0234f496-d2b7-00b6-17a4-b43e949b70a2/d1f3938c-28ca-462b-a688-c5f35b74a5bb/091024%20Supplemental%20Agenda.htm",  # noqa
        },
        {
            "title": "PDF",
            "href": "https://assets-us-01.kc-usercontent.com:443/0234f496-d2b7-00b6-17a4-b43e949b70a2/d8e39c4e-4f9d-4582-b357-572366d4619b/091024.pdf",  # noqa
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
