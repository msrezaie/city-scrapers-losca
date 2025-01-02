from datetime import datetime

import scrapy
from city_scrapers_core.constants import BOARD, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class LoscaCityPlanningSpider(CityScrapersSpider):
    name = "losca_City_Planning"
    agency = "Los Angeles City Planning"
    timezone = "America/Los_Angeles"

    start_urls = [
        "https://planning.lacity.gov/dcpapi2/meetings/api/all/commissions/{start_year}",
        "https://planning.lacity.gov/dcpapi2/meetings/api/all/boards/{start_year}",
        "https://planning.lacity.gov/dcpapi2/meetings/api/all/hearings/{start_year}",
    ]

    meetings_url = "https://planning.lacity.gov/about/commissions-boards-hearings"

    custom_settings = {
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [429, 500, 502, 503, 504],
        'DOWNLOAD_DELAY': 2,
    }

    def start_requests(self):
        """
        This spider retrieves meetings for the specified
        `start_year`, which is dynamically set to the
        current year.
        """
        current_year = datetime.now().year
        for url in self.start_urls:
            url = url.format(start_year=current_year)
            yield scrapy.Request(
                url=url,
                headers={"Accept": "application/json"},
                callback=self.parse,
            )

    def parse(self, response):
        try:
            data = response.json()
            if "Entries" not in data:
                self.logger.error("Missing 'Entries' field in response")
                return
            items = data["Entries"]
        except ValueError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            return

        for item in items:
            if not all(key in item for key in ["Type", "Date", "Address"]):
                self.logger.warning(
                    f"Skipping item due to missing required fields: {item}"
                )
                continue
            meeting = Meeting(
                title=item.get("Type", ""),
                description=item.get("Note", "").strip(),
                classification=self._parse_classification(item),
                start=parse(item.get("Date")),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self.meetings_url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_location(self, item):
        address = item.get("Address", "")
        address = address.replace("\n", "").replace("\r", "").strip()
        if address and "cancel" not in address.lower():
            return {
                "name": item.get("BoardName", ""),
                "address": address,
            }
        return {"name": "", "address": ""}

    def _parse_links(self, item):
        links = []

        for key in item.keys():
            if "Link" in key:
                href = item.get(key)
                if href:
                    links.append({"href": href, "title": key.replace("Link", "")})

        return links

    def _parse_classification(self, item):
        lower_text = item["Type"].lower()
        if "board" in lower_text:
            return BOARD
        elif "commission" in lower_text:
            return COMMISSION
        return NOT_CLASSIFIED
