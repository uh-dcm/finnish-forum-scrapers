import unittest
from uh_scrapy.spiders.vauva_spider import VauvaSpider
from tests.fake_response_unittest import mock_response, mock_response_from_file
from uh_scrapy.items import PostItem

class VauvaSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = VauvaSpider()

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
        results = self.spider.scrape_thread(mock_response_from_file('tests/assets/vauva_mock_thread.html', 'https://www.vauva.fi/keskustelu/2936023/mika-laihduttamisen-kannalta-terveellisiin-riisi-vai-peruna'))
        self._test_item_results(results, 20)

    def test_parse_threads(self):
        threads = list(self.spider.parse_threads(mock_response_from_file('tests/assets/vauva_mock_threads.html', 'https://www.vauva.fi/haku?keys=peruna')))
        self.assertEqual(len(threads), 11)


    
    