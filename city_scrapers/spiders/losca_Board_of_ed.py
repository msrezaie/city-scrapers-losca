import re

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class LoscaBoardOfEdSpider(CityScrapersSpider):
    name = "losca_Board_of_ed"
    agency = "Los Angeles Unified School District Board of Education"
    timezone = "America/Los_Angeles"
    # original URL was https://www.lausd.org/boe
    # they have an RSS feed. scrape that instead
    start_urls = [
        "https://www.lausd.org/site/RSS.aspx?DomainID=1057&ModuleInstanceID=73805&PageID=18628&PMIID=0"  # noqa
    ]

    def parse(self, response):
        """
        Parse meeting items from RSS feed.
        """
        location = {
            "name": "LAUSD Headquarters",
            "address": "333 South Beaudry Avenue, Board Room, Los Angeles, CA 90017",
        }
        for item in response.css("item"):
            # pdb.set_trace()
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=BOARD,
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """
        Parse meeting title. RSS feed titles always start with timestamp.
        Ex: '9/19/2024 10:00 AM - 1:00 PM Children... Early Education Committee'
        Remove timestamp from string and return title.
        """
        raw = item.css("title::text").get()
        no_stamp = raw.split()[6:-1]
        title = " ".join(no_stamp)
        return title

    def _parse_start(self, item):
        """
        Parse start datetime as a naive datetime object.
        pubdate::text gives us GMT, which is 7 hours ahead of PST.
        Get start date from title instead, since it is in the correct time zone.
        """
        raw = item.css("title::text").get()
        date = " ".join(raw.split()[0:3])
        return parse(date)

    def _parse_end(self, item):
        """
        Parse end datetime as a naive datetime object.
        End time is in title.
        """
        raw = item.css("title::text").get().split()
        date = raw[0]
        time = " ".join(raw[4:6])
        return parse(f"{date} {time}")

    def _parse_links(self, item):
        """
        Parse links. item.get() returns
        '...</title><link>https://www.lausd.org...EventDateID=73502<pubdate>...'
        This string does not have a closing </link> tag even though the source
        response does. This causes item.css('link') to return an empty tag.
        We must parse link another way. Try regex with split as fallback.
        """
        raw_html = item.get()
        match = re.search(r"<link>(.*?)<", raw_html, re.DOTALL)
        if match:
            link = match.group(1).strip()
        else:
            # Fallback to double split if regex doesn't match
            split = raw_html.split("<link>")[1]
            link = split.split("<pubdate>")[0].strip()

        return [{"title": "Meeting Details", "href": link}]
