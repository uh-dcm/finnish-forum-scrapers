from datetime import datetime
import scrapy
from pathlib import Path
import pandas as pd
from scrapy.http import FormRequest
from ..items import PostItem
import configparser

class HevostalliSpider(scrapy.Spider):

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
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    
    def parse(self, response):
        for forum in self.config["HEVOSTALLI_FORUMS"].values():
            url_start  = f'http://forum.hevostalli.net/list.php?f={forum}'
            yield scrapy.Request(url_start, callback=self.parse_threads)
        

    def parse_threads(self, response):
        threads = response.xpath('//tr[contains(@class, "dps_row")]')
        for thread in threads:
            link = thread.xpath('.//td[contains(@class, "PhorumListRow title")]/a/@href').get()
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.scrape_thread)

        yield from self.parse_threads_next_page(response)

    def parse_threads_next_page(self, response):
        next_page = response.xpath("//a[contains(@href, 'a=2')]/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_threads)


    def scrape_thread(self, response):
        i = 0
        ids= response.xpath(".//a/@name").getall()
        for comment in response.xpath("//td[@class='postbodywrap']"):
            post = PostItem()

            post["thread"] = response.xpath("//td[@class='postsubject']/span[@class='PhorumTableHeader']/text()").get().strip()

            post["author"] = comment.xpath(".//p[@class='PhorumMessage']/text()").getall()[1][1:].strip()
            
            body = comment.xpath(".//p[@class='PhorumMessage']/text()").getall()[3:]

            post["body"] = ' '.join([text.strip() for text in body if text.strip()])
            
            post["id"] = ids[i][6:]
            i+=1

            pre_time = comment.xpath(".//p[@class='PhorumMessage']/text()").getall()[2].strip()[11:].strip()
            parsed_date = datetime.strptime(pre_time, "%d.%m.%y %H:%M:%S")
            iso_date = parsed_date.strftime("%Y-%m-%dT%H:%M:%S")
            post["timestamp"] = iso_date

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



        