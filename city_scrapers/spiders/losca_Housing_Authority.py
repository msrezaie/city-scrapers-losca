from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class LoscaHousingAuthoritySpider(CityScrapersSpider):
    name = "losca_Housing_Authority"
    agency = "Housing Authority of the City of Los Angeles"
    timezone = "America/Los_Angeles"
    start_urls = ["https://www.hacla.org/en/bocfiles"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def parse(self, response):
        data = response.text
        print(f"HERE: {data}")

        # for item in response.css(".meetings"):
        #     meeting = Meeting(
        #         title=self._parse_title(item),
        #         description=self._parse_description(item),
        #         classification=self._parse_classification(item),
        #         start=self._parse_start(item),
        #         end=self._parse_end(item),
        #         all_day=self._parse_all_day(item),
        #         time_notes=self._parse_time_notes(item),
        #         location=self._parse_location(item),
        #         links=self._parse_links(item),
        #         source=self._parse_source(response),
        #     )

        #     meeting["status"] = self._get_status(meeting)
        #     meeting["id"] = self._get_id(meeting)

            # yield meeting
        yield None