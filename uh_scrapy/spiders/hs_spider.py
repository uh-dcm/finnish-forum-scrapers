import re
from datetime import datetime
from typing import Iterable
import scrapy
from pathlib import Path
import pandas as pd
import configparser
from ..items import PostItem


class HSSpider(scrapy.Spider):
    """Scraper for the Helsingin Sanomat (HS) comment section.

    Walks every configured news category on hs.fi, collects the article
    ids found on each section page and fetches the comments of each
    article from the HS commenting JSON API.
    """

    name = 'hs'
    start_urls = ["https://www.hs.fi"]

    def __init__(self, *args, **kwargs):
        super(HSSpider, self).__init__(*args, **kwargs)
        self.query = ''
        self.category = ''
        self.timefrom = ''
        self.timeto = ''
        self.sort = ''

        # Load the available news categories from config.ini.
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def parse(self, response):
        self.query = self.settings["QUERY"].lower()
        self.timefrom = self.settings["TIMEFROM"]
        self.timeto = self.settings["TIMETO"]

        # Visit every category page defined in the config.
        for cat_value in self.config["HS_CATEGORIES"].values():
            url = f'https://www.hs.fi/{cat_value}/'
            yield scrapy.Request(url, callback=self.parse_section, meta={'cat': cat_value})

    def parse_section(self, response):
        # Collect the unique article ids referenced on the category page.
        article_ids = set()
        for match in re.finditer(r'art-(\d+)\.html', response.text):
            article_ids.add(match.group(1))

        # Fetch the comment list for each article from the JSON API.
        for article_id in article_ids:
            url = f"https://www.hs.fi/api/commenting/hs/articles/{article_id}/comments"
            yield scrapy.Request(url, callback=self.scrape_thread, meta={'article_id': article_id})

    def scrape_thread(self, response):
        # Parse the comment JSON and emit one PostItem per comment.
        data = response.json()
        if data.get("totalComments", 0) == 0:
            return
        for comment in data['comments']:
            post = PostItem()
            post['id'] = comment["id"]
            post["thread"] = comment["articleId"]
            post["author"] = comment["userIdentity"]["displayName"]
            post["body"] = comment["comment"]
            # createdAt is a millisecond epoch timestamp; convert to the common format.
            post["timestamp"] = datetime.fromtimestamp(comment['createdAt'] / 1000).strftime("%Y-%m-%dT%H:%M:%S")
            yield post
