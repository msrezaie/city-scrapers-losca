from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.http import HtmlResponse
import pdb


class LoscaCityCouncilSpider(CityScrapersSpider):
    name = "losca_City_Council"
    agency = "Los Angeles City Council"
    timezone = "America/Chicago"
    start_urls = ["https://lacity.primegov.com/public/portal"]

    # use a headless browser to execute javascript and let data load
    def __init__(self, *args, **kwargs):
        super(LoscaCityCouncilSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        self.driver.get(response.url)
        # Wait for iframe to load, you might need to adjust the wait time or use WebDriverWait
        self.driver.implicitly_wait(5000)
        html = self.driver.page_source
        response = HtmlResponse(url=self.driver.current_url, body=html, encoding='utf-8')
        rows = response.css("#upcomingMeetingsContent tbody tr")
        # iframe_response = HtmlResponse(url=self.driver.current_url, body=iframe_source, encoding='utf-8')
        for row in rows:
            pdb.set_trace()
            title = row.css(".meeting-title").text
            print(f"title: {title}")
            meeting = Meeting(
                title=self._parse_title(row),
                description=self._parse_description(row),
                classification=self._parse_classification(row),
                start=self._parse_start(row),
                end=self._parse_end(row),
                all_day=self._parse_all_day(row),
                time_notes=self._parse_time_notes(row),
                location=self._parse_location(row),
                links=self._parse_links(row),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def closed(self, reason):
        self.driver.quit()

    def _parse_title(self, row):
        """Parse or generate meeting title."""
        title = row.find_element(By.CSS_SELECTOR, ".meeting-title").text
        return title

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
