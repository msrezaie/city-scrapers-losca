from city_scrapers_core.constants import CITY_COUNCIL
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse
import json

class LoscaCityCouncilSpider(CityScrapersSpider):
    name = "losca_City_Council"
    agency = "Los Angeles City Council"
    timezone = "America/Los_Angeles"
    # original URL https://clerk.lacity.gov/calendar
    # data is shown from an iframe https://lacity.primegov.com/public/portal
    # iframe loads data from API. "scrape" API instead
    # upcoming: lacity.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings?_=1726255032697
    # archived: lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year=2024
    start_urls = [
        "https://lacity.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings?_=1726255032697"
    ]

    def parse(self, response):
        """
        Parse API response.
        """

        # convert response to json
        data = json.loads(response.body)

        # hardcode location
        location = {
            "name": "Office of the City Clerk",
            "address": "200 N Spring St, Room 360, Los Angeles, CA 90012",
        }

        for obj in data:
            meeting = Meeting(
                title=obj['title'],
                description="",
                classification=CITY_COUNCIL,
                start=parse(obj['dateTime']),
                end=None,
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(obj),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_links(self, obj):
        """Parse or generate links."""
        return [{ "title": "video", "href": obj['videoUrl'] }]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
