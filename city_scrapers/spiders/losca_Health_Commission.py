from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class LoscaHealthCommissionSpider(CityScrapersSpider):
    name = "losca_Health_Commission"
    agency = "Los Angeles Health Commission"
    timezone = "America/Los_Angeles"
    committee_id: int = 6
    start_year: int = 2024
    default_location = {
        "address": "200 N Spring St, Room 340 (CITY HALL) Los Angeles, CA 90012",
        "name": "Los Angeles City Health Commission",
    }
    start_urls = [
        f"https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetingsByCommitteeId?year={start_year}&committeeId={committee_id}"  # noqa
    ]

    def parse(self, response):
        """
        This spider retrieves meetings for the specified `start_year`.
        Update `start_year` to change the target year.
        """
        try:
            items = response.json()
            if not isinstance(items, list):
                self.logger.error(f"Expected list of items, got {type(items)}")
                return

            for item in items:
                required_fields = ["title", "dateTime", "videoUrl", "documentList"]
                if not all(field in item for field in required_fields):
                    missing_fields = [
                        field for field in required_fields if field not in item
                    ]
                    self.logger.warning(
                        f"Missing required fields {missing_fields} in item with id {item.get('id', 'N/A')}"  # noqa
                    )
                    continue

                meeting = Meeting(
                    title=self._parse_title(item),
                    description="",
                    classification=COMMISSION,
                    start=self._parse_start(item),
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self.default_location,
                    links=self._parse_links(item),
                    source=response.url,
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting
        except ValueError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item["title"] if item["title"] else ""

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        try:
            return parse(item["dateTime"])
        except (ValueError, TypeError) as e:
            self.logger.error(f"Failed to parse datetime '{item.get('dateTime')}': {e}")
            return None

    def _parse_links(self, item):
        """Parse or generate links.

        Link types:
        - videoUrl: Direct link to meeting video
        - compileOutputType 3: Meeting template link
        - compileOutputType 1: Compiled document link
        """
        COMPILE_OUTPUT_TYPES = {
            3: "https://lacity.primegov.com/Portal/Meeting?meetingTemplateId={}",
            1: "https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={}&compileOutputType=1",  # noqa
        }
        data = []
        if item.get("videoUrl"):
            data.append({"href": item["videoUrl"], "title": "Video Link"})

        for document in item.get("documentList", []):
            if not document:
                continue
            output_type = document.get("compileOutputType")
            template_id = document.get("templateId")
            template_name = document.get("templateName")
            if output_type in COMPILE_OUTPUT_TYPES and template_id and template_name:
                data.append(
                    {
                        "href": COMPILE_OUTPUT_TYPES[output_type].format(template_id),
                        "title": template_name,
                    }
                )
        return data
