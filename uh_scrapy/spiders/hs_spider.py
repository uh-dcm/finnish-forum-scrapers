from datetime import datetime
from typing import Iterable
import scrapy
from pathlib import Path
import pandas as pd
import constants
import time
from ..items import PostItem
import configparser


class HSSpider(scrapy.Spider):
    name= 'hs'
    start_urls = ["https://www.hs.fi"]
    
    def __init__(self, *args, **kwargs):
        super(HSSpider, self).__init__(*args, **kwargs)
        self.query = ''
        self.category = ''
        self.timefrom = ''
        self.timeto = ''
        self.sort = ''

        self.count = 50
        self.offset = 0
        self.limit = 0
        
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    #convert date string to epoch time
    def convert_to_epoch_ms(self, date_string):
        # Back to date object
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        
        # Convert the datetime object to epoch time in seconds
        epoch_time = int(time.mktime(date_obj.timetuple()))
        
        # Multiply by 1000 to get milliseconds
        epoch_ms = epoch_time * 1000
        return epoch_ms

    #Function to turn the search parameters into a valid url 
    def query_to_url(self, count, offset):
        APIurl = f'https://www.hs.fi/api/search/{self.query}/{self.category}/custom/{self.sort}/{offset}/{count}/{self.timefrom}/{self.timeto}/keyword'
        return APIurl  

    #initial request
    def parse(self, response):

        self.query = self.settings["QUERY"].replace(" ", "%20")
        self.timefrom = self.convert_to_epoch_ms(self.settings["TIMEFROM"])
        self.timeto = self.convert_to_epoch_ms(self.settings["TIMETO"])
        self.sort = 'rel'
        self.limit = 0

        for cat_value in self.config["HS_CATEGORIES"].values():
            self.offset = 0
            self.category = cat_value
            url = self.query_to_url(self.count, self.offset)
            yield scrapy.Request(url, callback=self.parse_threads, meta={'cat': cat_value, 'offset': 0})
    
 
    
    # Function to collect thread ids
    def parse_threads(self, response):
        
        self.offset = response.meta['offset']
        data = response.json()
        if data != []:
            for id in [entry['id'] for entry in data]:
                url = f"https://www.hs.fi/api/commenting/hs/articles/{id}/comments"
                yield scrapy.Request(url, callback=self.scrape_thread)
        
        yield from self.parse_threads_next_page(response)

    def parse_threads_next_page(self, response):
        if self.limit==0 or self.offset+self.count<self.limit:
            self.offset = self.offset + self.count
            self.category = response.meta['cat']
            APIurl = self.query_to_url(self.count, self.offset)
            yield scrapy.Request(APIurl, callback=self.parse_threads, meta={'cat': response.meta['cat'], 'offset': self.offset})

    # Function to scrape comments from thread
    def scrape_thread(self, response):
        data = response.json()
        if data["totalComments"] != 0:
            for comment in data['comments']:
                post = PostItem()
                post['id'] = comment["id"]
                post["thread"] = comment["articleId"]
                post["author"] = comment["userIdentity"]["displayName"]
                post["body"] = comment["comment"]
                post["timestamp"] = datetime.fromtimestamp(comment['createdAt'] / 1000).strftime("%Y-%m-%dT%H:%M:%S")
                yield post


    def scrape_next_thread(self, response):
        pass

    # Function to make an appropriate filename
    def make_filename(self):
        argstr = '_'.join(self.filename.values())
        dt = datetime.now()
        filename_date_string = dt.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'scrapedcontent/hs_{filename_date_string}_{argstr}.csv'
        return filename

    # Function to save scraped data to csv
    def to_4cat_csv(self, comments, filename):
        df = pd.DataFrame( comments )
        newdf = pd.DataFrame()
        newdf['body'] = df['comment']
        newdf['author'] = df['userIdentity'].apply( lambda userIdentity: userIdentity['displayName'] )
        newdf['timestamp'] = df['createdAt'].apply(  lambda date: datetime.fromtimestamp(  date/1000 ).strftime("%Y-%m-%d %H:%M:%S") )
        newdf['id'] = df['id']
        newdf['thread'] = df['articleId']
        

        newdf.to_csv(filename)
    

    # Make filename and save data after spider is done
    def closed(self, reason):
        pass
        # name = self.make_filename()
        # self.to_4cat_csv(self.comments, name)

        