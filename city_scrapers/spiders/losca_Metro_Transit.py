from city_scrapers_core.constants import BOARD, CITY_COUNCIL, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class LoscaMetroTransitSpider(LegistarSpider):
    name = "losca_Metro_Transit"
    agency = "Los Angeles Metro Transit"
    timezone = "America/Los_Angeles"
    start_urls = ["https://metro.legistar.com/Calendar.aspx"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def parse_legistar(self, events):
        for event in events:
            start = self.legistar_start(event)
            if start:
                meeting = Meeting(
                    title=event.get("Name", {}).get("label", "No Title"),
                    description="",
                    classification=self._parse_classification(event),
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self._parse_location(event),
                    links=self._parse_links(event),
                    source=self.legistar_source(event),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        name_label = item.get("Name", {}).get("label", "").lower()
        if "committee" in name_label:
            return COMMITTEE
        if "board" in name_label:
            return BOARD
        if "council" in name_label:
            return CITY_COUNCIL
        return NOT_CLASSIFIED

    def _parse_links(self, item):
        """Parse or generate links to additional information."""
        links = []

        if isinstance(item.get("Name"), dict) and item["Name"].get("url"):
            links.append(
                {
                    "href": item["Name"]["url"],
                    "title": item["Name"].get("label", "Meeting Details"),
                }
            )

        if isinstance(item.get("Agenda"), dict) and item["Agenda"].get("url"):
            links.append(
                {
                    "href": item["Agenda"]["url"],
                    "title": item["Agenda"].get("label", "Agenda"),
                }
            )

        if isinstance(item.get("iCalendar"), dict) and item["iCalendar"].get("url"):
            links.append({"href": item["iCalendar"]["url"], "title": "iCalendar"})

        if (
            isinstance(item.get("Audio"), dict)
            and item["Audio"].get("url")
            and item["Audio"].get("label") != "Not\xa0available"
        ):
            links.append(
                {"href": item["Audio"]["url"], "title": item["Audio"]["label"]}
            )

        return links

    def _parse_location(self, item):
        """Parse or generate location."""
        if isinstance(item["Meeting Location"], dict):
            return {
                "address": item["Meeting Location"]["label"],
                "name": item["Name"]["label"],
            }
        else:
            return item["Meeting Location"]
