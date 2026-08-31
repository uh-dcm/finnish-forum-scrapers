from datetime import datetime
import scrapy
from pathlib import Path
import pandas as pd
from ..items import PostItem
from scrapy.utils.project import get_project_settings

class VauvaSpider(scrapy.Spider):
    """Scraper for the Vauva.fi discussion forum.

    Searches for threads matching the configured QUERY, follows the
    thread search results and extracts every comment posted in those
    threads.
    """

    name = "vauva"
    start_urls = ['https://www.vauva.fi/']

    def __init__(self, *args, **kwargs):
        super(VauvaSpider, self).__init__(*args, **kwargs)
        self.query = ""

    def parse(self, response):
        # Build the search URL from the configured query and hand the
        # result page over to parse_threads.
        self.query = self.settings["QUERY"]
        url_start = f'https://www.vauva.fi/haku?keys={self.query}&sort&searchpage'
        yield scrapy.Request(url_start, callback=self.parse_threads)
    
    def parse_threads(self, response):
        # Iterate over every search result and follow the link to the thread.
        for thread in response.xpath("//div[@class='result']"):
            link = thread.xpath(".//a[contains(@href, 'replies')]/@href").get()
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.scrape_thread)

        yield from self.parse_threads_next_page(response)

    def parse_threads_next_page(self, response):
        # Follow the "Seuraava" (next) pagination link, if present.
        next_page = response.xpath('//a/span[text()="Seuraava"]/../@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_threads)

    def scrape_thread(self, response):
        # Extract every comment from the thread page into a PostItem.
        for comment in response.xpath('//div[contains(@class, "comment comment")]'):
            post = PostItem()
            post['id'] = comment.xpath('.//div[@id]/@id').get()
            post["thread"] = response.xpath("//meta[contains(@property, 'og:site_name')]//@content").get()
            author = comment.xpath(".//article[@class='user user--compact']//text()").getall()
            post["author"] = ''.join(item.strip() for item in author if item.strip())
            post["body"] = ''.join(comment.xpath('.//div[contains(@class, "content my")]/*').getall())
            # Normalise the ISO timestamp to the common "%Y-%m-%dT%H:%M:%S" format.
            post["timestamp"] = datetime.fromisoformat(''.join(comment.xpath(".//div[contains(@class, 'flex justify-end')]/div/time/@datetime").getall())).strftime('%Y-%m-%dT%H:%M:%S')
            
            yield post
        
        yield from self.scrape_threads_next_page(response)

    def scrape_threads_next_page(self, response):
        # Follow the pagination link to the next page of comments.
        next_page =  response.xpath('//a/span[text()="Seuraava"]/../@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.scrape_thread)

    def closed(self, reason):
        # Hook called when the spider finishes; currently unused.
        pass




        