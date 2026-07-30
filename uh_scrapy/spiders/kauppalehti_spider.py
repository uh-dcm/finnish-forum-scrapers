from datetime import datetime
import scrapy
from pathlib import Path
import pandas as pd
from scrapy.http import FormRequest
import logging
import configparser
from ..items import PostItem

class KauppalehtiSpider(scrapy.Spider):

    name = "kauppalehti"
    start_urls = ['https://keskustelu.kauppalehti.fi/search/']

    def __init__(self, *args, **kwargs):
        super(KauppalehtiSpider, self).__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    
    def parse(self, response):
        self.query = self.settings["QUERY"].replace(" ", "%20")

        _xfToken = response.css("input[name='_xfToken']::attr(value)").get()
        if not _xfToken:
            self.logger.error("Could not retrieve _xfToken")
            return
        formdata = {
            'keywords': self.query,
            'c[title_only]': '0',
            'c[newer_than]': self.settings["TIMEFROM"],
            'c[older_than]': self.settings["TIMETO"],
            'c[min_reply_count]': '0',
            'order': 'date',
            'grouped': '1',
            '_xfToken': _xfToken,
        }
        yield FormRequest(
            url='https://keskustelu.kauppalehti.fi/search/search',
            formdata=formdata,
            method='POST',
            callback=self.parse_threads
        )


    def parse_threads(self, response):
        print("Parsing threads now")
        threads = response.xpath("//li[contains(@class, 'block-row--separated')]")
        for thread in threads:
            link = thread.xpath(".//h3[@class='contentRow-title']/a/@href").get()
            url = response.urljoin(link)
            thread_name = thread.xpath(".//h3[@class='contentRow-title']/a/text()").getall()
            thread_name = ' '.join([text.strip() for text in thread_name if text.strip()]),
            yield scrapy.Request(url, callback=self.scrape_thread, meta={'thread': thread_name})

        yield from self.parse_threads_next_page(response)



    def parse_threads_next_page(self, response):
        next_page = response.xpath("//a[contains(@class, 'pageNav-jump--next')]/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_threads)


    def scrape_thread(self, response):
        thread = response.xpath("//div[@class='p-title ']/h1/text()").get()
        for comment in response.xpath("//div[@class='message-inner']"):
            post = PostItem()
            body = comment.xpath(".//article[@class='message-body js-selectToQuote']//div[@class='bbWrapper']//text()").getall()
            post["thread"] = thread
            post["author"] = comment.xpath(".//h4[@class='message-name']/a//text()").get()
            post["body"] = ' '.join([text.strip() for text in body if text.strip()])
            post["id"] = comment.xpath(".//a[contains(@class, 'message-attribution-gadget')]/@data-href").re_first(r'/posts/(\d+)/')
            post['timestamp'] = comment.xpath(".//time[@class='u-dt']/@datetime").get()
            yield post
        yield from self.scrape_thread_next_page(response)

    #check if the next page exists
    def scrape_thread_next_page(self, response):
        next_page = response.xpath("//a[contains(@class, 'pageNav-jump--next')]/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.scrape_thread)




   # Function to make an appropriate filename
    def make_filename(self):
        argstr = '_'.join(self.search)
        dt = datetime.now()
        filename_date_string = dt.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f'scrapedcontent/kauppalehti_{filename_date_string}_{argstr}.csv'
        return filename

    # Function to save scraped data to csv
    def to_4cat_csv(self, comments , filename):
        df = pd.DataFrame( comments ) 
        df.to_csv( filename )

    # Make filename and save data after spider is done
    def closed(self, reason):
        pass




        