from datetime import datetime
import scrapy
from pathlib import Path
import pandas as pd
from scrapy.http import FormRequest
from ..items import PostItem
import configparser

class HevostalliSpider(scrapy.Spider):
    """Scraper for the forum.hevostalli.net discussion forum.

    Visits every forum section defined in the config, follows the thread
    listings and extracts each post found on the thread pages.
    """

    name = 'hevostalli'
    start_urls = ['http://forum.hevostalli.net/']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'LOG_LEVEL': 'DEBUG',
        'ROBOTSTXT_OBEY': False,  # Temporarily disable robots.txt obeying
    }

    def __init__(self, *args, **kwargs):
        super(HevostalliSpider, self).__init__(*args, **kwargs)
        self.formdata = []
        self.items = []
        # Load the forum sections from config.ini.
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    
    def parse(self, response):
        # Start from each configured forum section.
        for forum in self.config["HEVOSTALLI_FORUMS"].values():
            url_start  = f'http://forum.hevostalli.net/list.php?f={forum}'
            yield scrapy.Request(url_start, callback=self.parse_threads)
        

    def parse_threads(self, response):
        # Follow every thread link found in the forum listing.
        threads = response.xpath('//tr[contains(@class, "dps_row")]')
        for thread in threads:
            link = thread.xpath('.//td[contains(@class, "PhorumListRow title")]/a/@href').get()
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.scrape_thread)

        yield from self.parse_threads_next_page(response)

    def parse_threads_next_page(self, response):
        # Follow the pagination link to the next listing page, if present.
        next_page = response.xpath("//a[contains(@href, 'a=2')]/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_threads)


    def scrape_thread(self, response):
        # Grab the thread title from the page header.
        thread = response.xpath("//td[@class='postsubject']/span[@class='PhorumTableHeader']/text()").get()
        if thread:
            thread = thread.strip()
        # Post ids are stored in the name attributes of anchor tags.
        ids = response.xpath(".//a/@name").getall()
        for i, comment in enumerate(response.xpath("//td[@class='postbodywrap']")):
            post = PostItem()
            post["thread"] = thread

            # The post data lives in the paragraph elements: author,
            # timestamp and message body are positional fragments.
            texts = comment.xpath(".//p[@class='PhorumMessage']/text()").getall()

            if len(texts) > 1:
                # The author is the last fragment split by the nbsp char.
                author_text = texts[1]
                post["author"] = author_text.split('\xa0')[-1].strip() if '\xa0' in author_text else author_text.strip()

            if len(texts) > 3:
                # The message body starts at the fourth fragment.
                body = texts[3:]
                post["body"] = ' '.join([t.strip() for t in body if t.strip()])

            if i < len(ids) and ids[i] and len(ids[i]) > 6:
                # Strip the leading 6 chars of the name attribute to get the post id.
                post["id"] = ids[i][6:]

            if len(texts) > 2:
                # Parse the timestamp from the "dd.mm.yy hh:mm:ss" format.
                date_text = texts[2].strip()
                paiva = date_text.split('\xa0')[-1].strip() if '\xa0' in date_text else date_text
                if len(paiva) > 10:
                    paiva = paiva[-17:].strip()
                try:
                    parsed_date = datetime.strptime(paiva, "%d.%m.%y %H:%M:%S")
                    post["timestamp"] = parsed_date.strftime("%Y-%m-%dT%H:%M:%S")
                except (ValueError, IndexError):
                    pass

            # Only emit posts that could be parsed with a timestamp.
            if post.get("timestamp"):
                yield post



    def scrape_thread_next_page(self, response):
        pass



   # Function to make an appropriate filename
    def make_filename(self):
        argstr = '_'.join(self.formdata)
        dt = datetime.now()
        filename_date_string = dt.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'scrapedcontent/kaksplus.fi_{filename_date_string}_{argstr}'
        return filename



        