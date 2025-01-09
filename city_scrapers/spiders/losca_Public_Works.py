from datetime import datetime

import requests
import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparse
from dateutil.relativedelta import relativedelta


class LoscaPublicWorksSpider(CityScrapersSpider):
    name = "losca_Public_Works"
    agency = "Los Angeles Board of Public Works"
    timezone = "America/Los_Angeles"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    api_access_url = "https://api.lacity.org/oauth/accesstoken"
    api_access_token = (
        "Basic bTQ5VXdhcmxFbzVBUm9IcjNSYkd1RzdvOHdCQ2ZxSHM6WUdweXREc3Y0Q29pVlNncw=="
    )
    api_meetings_url = (
        "https://api.lacity.org/city_calendar?_format=json&display_id=rest_export&"
        "start={start}&eventtype=ENS%20-%20Meeting%20-%20Board&department=Board%20of"
        "%20Public%20Works&offset={offset}&items_per_page=15"
    )
    api_meta_url = (
        "https://api.lacity.org/city_calendar/meta?_format=json&"
        "display_id=rest_export_meta&start={start}&eventtype=ENS"
        "%20-%20Meeting%20-%20Board&department=Board%20of%20Public"
        "%20Works&items_per_page=500"
    )

    meeting_address = {
        "address": "200 N Spring St, Los Angeles, CA 90012",
        "name": "City Hall",
    }

    def start_requests(self):
        """
        The meeting information for this organization is retrieved
        from its API, which requires a 'Bearer' token for access.
        The API limits each request to a maximum of 15 meetings (a
        hardcoded parameter). The '_parse_meetings' function manages
        the logic for sending concurrent requests based on the total
        number of meeting items obtained from the 'api_meta_url'.
        Meetings are fetched starting six months in the past up to
        the current date, with no defined end date.
        """
        current_date = datetime.now()
        six_months_ago = current_date - relativedelta(months=6)
        start = six_months_ago.date()
        access_token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        yield scrapy.Request(
            self.api_meta_url.format(start=start),
            headers=headers,
            callback=self._parse_meetings,
            meta={"start": start, "headers": headers},
        )

    def _get_access_token(self):
        try:
            api_access_body = requests.post(
                self.api_access_url,
                headers={"Authorization": self.api_access_token},
                data={"grant_type": "client_credentials"},
            ).json()

            access_token = api_access_body.get("access_token")
            return access_token
        except requests.RequestException as e:
            self.logger.error("Failed to retrieve access token: %s", e)
            return

    def _parse_meetings(self, response):
        meetings_length = len(response.json())
        offset = 15
        start = response.meta.get("start")
        headers = response.meta.get("headers")
        for i in range(0, meetings_length, offset):
            yield scrapy.Request(
                self.api_meetings_url.format(start=start, offset=i),
                headers=headers,
                callback=self.parse,
            )

    def parse(self, response):
        meetings = response.json()
        for item in meetings:
            meeting = Meeting(
                title=self._parse_title(item),
                description=item["description"],
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="Please check meeting source for time and location details",
                location=self.meeting_address,
                links=self._parse_links(item),
                source=item["url"],
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        title = item["title"].replace("*", "").strip()
        return title

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        datetime_str = dateparse(item["start"])
        datetime_naive = datetime_str.replace(tzinfo=None)
        return datetime_naive

    def _parse_links(self, item):
        agenda_url = item.get("informationurl")
        return [{"href": agenda_url, "title": "Agenda"}] if agenda_url else []
