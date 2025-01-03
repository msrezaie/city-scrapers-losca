import re

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
                meeting_location, description = self._parse_location(event)
                meeting = Meeting(
                    title=event.get("Name", {}).get("label", "No Title"),
                    description=description,
                    classification=self._parse_classification(event),
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=meeting_location,
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
        """
        The location format of the meetings is not consistent.
        It is returned as a string or a dictionary. The string
        format at times contains the location/type of the held
        meeting. This function parses that and returns it as the
        meeting description.
        """
        location = {"name": "", "address": ""}
        description = ""
        print(f"ITEM: {item}")
        if isinstance(item["Meeting Location"], dict):
            location["name"] = item["Name"]["label"]
            location["address"] = item["Meeting Location"]["label"]
        else:
            meeting_location = item["Meeting Location"]
            meeting_location = (
                meeting_location.replace("(", "").replace(")", "").strip()
            )

            splits = re.split(r"(\b\d{5}\b)", meeting_location)
            if len(splits) > 2:
                if "floor" in splits[2].lower() or "room" in splits[2].lower():
                    room = splits[2].replace("\r\n", "").lstrip(", ").strip()
                    address = f"{room}, {splits[0].strip()} {splits[1].strip()}"
                    location["name"] = item["Name"]["label"]
                    location["address"] = address
                else:
                    address = f"{splits[0].strip()} {splits[1].strip()}"
                    description = splits[2].strip()
                    location["name"] = item["Name"]["label"]
                    location["address"] = address

        return location, description
