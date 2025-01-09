from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta


class LoscaHousingAuthoritySpider(CityScrapersSpider):
    name = "losca_Housing_Authority"
    agency = "Housing Authority of the City of Los Angeles"
    timezone = "America/Los_Angeles"
    start_urls = ["https://www.hacla.org/en/bocfiles"]

    def parse(self, response):
        """
        Parse meetings from the meetings section.
        """
        # location from https://www.hacla.org/en/about-us/contact-us
        location = {
            "name": "HACLA",
            "address": "2600 Wilshire Blvd. Los Angeles, CA 90057",
        }
        for item in response.css(".views-element-container .views-row"):
            start_date = self._parse_start(item)
            cutoff = datetime.now() - relativedelta(months=6)
            if start_date and start_date > cutoff:
                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=BOARD,
                    start=self._parse_start(item),
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=location,
                    links=self._parse_links(item),
                    source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        text = item.css(".views-field-title .field-content::text").get()
        title = " ".join(text.split()[1:])
        return title

    def _parse_start(self, item):
        """
        Parse start datetime as a naive datetime object.
        Website says "meetings indicated herein begin at 9:00 a.m"
        """
        text = item.css(".views-field-title .field-content::text").get()
        if text:
            date = text.split()[0]
            return parse(f"{date} 9am")
        else:
            return None

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        # add minutes links if any
        for link in item.css(".views-field-field-action-minutes a"):
            href = link.css("::attr(href)").get()
            links.append({"title": "Minutes", "href": href})
        # add audio links if any
        for link in item.css(".views-field-field-audio a"):
            href = link.css("::attr(href)").get()
            links.append({"title": "Audio", "href": href})

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
