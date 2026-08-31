from datetime import datetime
from typing import Iterable
import scrapy
from pathlib import Path
import pandas as pd
import constants
import configparser
from ..items import PostItem


class YleSpider(scrapy.Spider):
    """Scraper for the Yle.fi comment sections.

    Queries the Yle search API for articles matching the configured
    search terms, time window, category and language, then fetches the
    comments of every matched article from the Yle comments API.
    """

    name= 'yle'
    start_urls = ['https://yle.fi/']
    
    def __init__(self, *args, **kwargs):
        super(YleSpider, self).__init__(*args, **kwargs)
        self.count = 50
        # Load the search categories and languages from config.ini.
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        

    # Function to turn the search parameters into a valid url 
    def query_to_url(self, count, offset):
        # Build the Yle search API url from the configured parameters.
        app_id = 'hakuylefi_v2_prod'
        app_key = '4c1422b466ee676e03c4ba9866c0921f'
        # Join only the non-empty search parameters with '&'.
        searchstr = "&".join([a for a in self.search if a != ""])
        APIurl = f'https://yle-fi-search.api.yle.fi/v1/search?app_id={app_id}&app_key={app_key}&limit={count}&offset={offset}&type=article&{searchstr}&time=custom'
        return APIurl

    
    def parse(self, response):
        # Assemble the query parameters from the spider settings.
        query = "query=" + self.settings["QUERY"].replace(" ", "%20")
        timeFrom = "timeFrom=" + self.settings["TIMEFROM"]
        timeTo = "timeTo=" + self.settings["TIMETO"]

        self.count = 50
        self.limit = 100

        self.comments = []

        # Run a search for every combination of category and language.
        for cat_value in self.config["YLE_CATEGORIES"].values():
            for lang_value in self.config["YLE_LANGUAGE"].values():
                self.search = [query, cat_value, timeFrom, timeTo, lang_value]
                self.offset = 0
                url = self.query_to_url(self.count, self.offset)
                yield scrapy.Request(url, callback=self.parse_threads, meta={'search': list(self.search), 'offset': 0})
 
    
    # Function to collect thread ids
    def parse_threads(self, response):
        print('parsing')
        data = response.json()
        self.total_count = data['meta']['count']
        self.search = response.meta['search']
        self.offset = response.meta['offset']
        # Fetch the comments of every article returned by the search.
        if self.total_count != 0:
            for id in [entry['id'] for entry in data['data']]:
                app_key = 'sfYZJtStqjcANSKMpSN5VIaIUwwcBB6D'
                app_id = 'yle-comments-plugin'
                url = f"https://comments.api.yle.fi/v1/topics/{id}/comments/accepted?app_id={app_id}&app_key={app_key}&parent_limit=100"
                yield scrapy.Request(url, callback=self.scrape_thread)

        yield from self.parse_threads_next_page(response)

    def parse_threads_next_page(self,response):
        # Request the next page of search results while there are more left.
        if self.offset+self.count<self.total_count:
            self.offset = self.offset + self.count
            APIurl = self.query_to_url(self.count, self.offset)
            yield scrapy.Request(APIurl, callback=self.parse_threads, meta={'search': self.search, 'offset': self.offset})

    # Function to scrape comments from thread
    def scrape_thread(self, response):
        data = response.json()    
        # The API returns a 'notifications' object when there is no data.
        if 'notifications' not in data:
            for comment in data:
                print(comment)
                post = PostItem()
                post['author'] = comment['author'] 
                post['body'] = comment['content']
                post['timestamp'] = comment['createdAt']
                post['id'] = comment['id']
                post['thread'] = comment['topicExternalId']
                yield post
    
    def scrape_thread_next_page(self,response):
        pass

    # Function to make an appropriate filename
    def make_filename(self):
        argstr = '_'.join(self.filename)
        dt = datetime.now()
        filename_date_string = dt.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'scrapedcontent/yle_{filename_date_string}_{argstr}.csv'
        return filename

    # Function to save scraped data to csv
    def to_4cat_csv(self, comments , filename):
        # Reorder the comment columns into the 4CAT format and save to csv.
        df = pd.DataFrame( comments )
        newdf = pd.DataFrame()
        newdf['body'] = df['content']
        newdf['author'] = df['author']
        newdf['timestamp'] = df['createdAt'].apply(  lambda date: datetime.strptime(  date , "%Y-%m-%dT%H:%M:%S%z" ).strftime("%Y-%m-%d %H:%M:%S") )
        newdf['id'] = df['id']
        newdf['thread'] = df['topicExternalId']
        newdf.to_csv( filename )

    # Make filename and save data after spider is done
    def closed(self, reason):
        pass

        