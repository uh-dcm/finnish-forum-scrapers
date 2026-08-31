# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import datetime
from scrapy.exceptions import DropItem

from uh_scrapy.text_utils import matches, simple_matches


class uh_scrapyPipeline:
    def process_item(self, item):
        return item

class TimestampFilterPipeline:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        start_date_str = crawler.settings.get('TIMEFROM')
        end_date_str = crawler.settings.get('TIMETO')
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        start_date=start_date.replace(hour=0, minute=0, second=0)
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        end_date=end_date.replace(hour=0, minute=0, second=0)

        return cls(start_date, end_date)

    def process_item(self, item):
        adapter = ItemAdapter(item)
        iso_date = adapter['timestamp']

        try:
            parsed_date = datetime.datetime.fromisoformat(iso_date)
        except ValueError:
            try:
                parsed_date = datetime.datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise DropItem(f"Invalid timestamp format: {iso_date}")

        if parsed_date.tzinfo is not None:
            parsed_date = parsed_date.replace(tzinfo=None)

        if self.start_date <= parsed_date <= self.end_date:
            return item
        else:
            raise DropItem(f"Item does not pass the filter(Timestamp filter)")
        
class BodyFilterPipeline:
    def __init__(self,  query, use_lemmatization=True):
        self.query = query
        self.use_lemmatization = use_lemmatization

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):

        query = crawler.settings.get('QUERY')
        use_lemmatization = crawler.settings.getbool('USE_LEMMATIZATION', True)

        return cls(query, use_lemmatization)

    def process_item(self, item):
        
        adapter = ItemAdapter(item)
        body = adapter['body']

        if self.use_lemmatization:
            found = matches(self.query, body)
        else:
            found = simple_matches(self.query, body)

        if found:
            return item  # Keep the item
        else:
            raise DropItem(f"Item does not pass the filter(Body filter)")

