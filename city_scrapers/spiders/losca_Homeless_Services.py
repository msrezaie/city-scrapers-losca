from datetime import datetime
from urllib.parse import urljoin

from city_scrapers_core.constants import (
    BOARD,
    CITY_COUNCIL,
    COMMISSION,
    COMMITTEE,
    NOT_CLASSIFIED,
)
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class LoscaHomelessServicesSpider(CityScrapersSpider):
    name = "losca_Homeless_Services"
    agency = "Los Angeles Homeless Services Authority"
    timezone = "America/Los_Angeles"
    start_urls = ["https://www.lahsa.org/events"]

    def parse(self, response):
        """
        Parse upcoming meetings for LAHSA.
        """
        for item in response.css(".col-lg-8 .list-group a"):
            # parse classification first
            # we need it for location
            classification = self._parse_classification(item)
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=classification,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="Start time in Event Link",
                location=self._parse_location(classification),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse meeting title."""
        return item.css(".h6::text").get()

    def _parse_classification(self, item):
        """Parse classification from allowed options."""
        title = item.css(".h6::text").get().lower()
        if "board" in title:
            return BOARD
        elif "council" in title:
            return CITY_COUNCIL
        elif "commission" in title:
            return COMMISSION
        elif "committee" in title:
            return COMMITTEE
        else:
            return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        datestring = item.css(".text-secondary::text").get()
        # sometimes datestring is "NEXT WEDNESDAY"
        # use fuzzy parser to handle this kind of input
        # example: if today is 12/20/2024, "NEXT WEDNESDAY" returns "12/25/2024"
        # sometimes datestring is "January 08" which returns "1/8/2024"
        # but we need it to return "1/8/2025"
        date = parse(datestring, fuzzy=True)
        # datetime.today() returns date and time
        # zero out the time part of the object to handle edge cases like
        # a meeting happening that same day
        if date < datetime.today().replace(hour=0, minute=0, second=0, microsecond=0):
            date = date.replace(year=date.year + 1)
        return date

    def _parse_location(self, classification):
        """
        Generate location from classification.
        After inspecting the locations from different agency meetings,
        it appears only city council meetings occur at a different address.
        """
        # default location
        location = {
            "name": "LAHSA (check Event Link)",
            "address": "707 Wilshire Blvd, 10th Floor, Los Angeles, CA 90017",
        }

        # override if classification is city council
        if classification == CITY_COUNCIL:
            location["name"] = "City Council (check Event Link)"
            location["address"] = (
                "637 Wilshire Blvd, 1st Floor Commission Room, Los Angeles, CA 90017"  # noqa
            )

        return location

    def _parse_links(self, item):
        """Parse links."""
        base_url = "https://www.lahsa.org/"
        href = item.css("::attr(href)").get()
        url = urljoin(base_url, href)
        return [{"title": "Event Link", "href": url}]
