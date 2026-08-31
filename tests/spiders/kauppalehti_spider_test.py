import unittest
from uh_scrapy.spiders.kauppalehti_spider import KauppalehtiSpider
from tests.fake_response_unittest import mock_response, mock_response_from_file
from uh_scrapy.items import PostItem

class KauppalehtiSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = KauppalehtiSpider()

    def _test_item_results(self, results, expected_length):
        count = 0
        permalinks = set()
        for item in results:
            if isinstance(item, PostItem):
                self.assertIsNotNone(item['author'])
                self.assertIsNotNone(item['thread'])
                self.assertIsNotNone(item['body'])
                self.assertIsNotNone(item['id'])
                self.assertIsNotNone(item['timestamp'])
                permalinks.add(item['id'])
                count += 1
        self.assertEqual(count, expected_length)
        self.assertEqual(len(permalinks), count)

    def test_scrape_thread(self):
        results = self.spider.scrape_thread(mock_response_from_file('tests/assets/kauppalehti_mock_thread.html', 'https://keskustelu.kauppalehti.fi/threads/venajan-hyokkays-ukrainaan.248392/'))
        self._test_item_results(results, 20)

    def test_parse_threads(self):
        threads = list(self.spider.parse_threads(mock_response_from_file("tests/assets/kauppalehti_mock_threads.html", "https://keskustelu.kauppalehti.fi/search/1200696/?q=peruna&t=post&o=relevance&g=1")))
        self.assertEqual(len(threads), 21)


    
    