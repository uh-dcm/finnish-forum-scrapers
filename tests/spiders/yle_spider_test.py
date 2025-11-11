import unittest
from uh_scrapy.spiders.yle_spider import YleSpider
from tests.fake_response_unittest import mock_response, mock_response_from_file
from uh_scrapy.items import PostItem

class YleSpiderTest(unittest.TestCase):
    def setUp(self):
        self.spider = YleSpider()

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
        results = self.spider.scrape_thread(mock_response_from_file('tests/assets/yle_mock_thread.html', 'https://comments.api.yle.fi/v1/topics/74-20127553/comments/accepted?app_id=yle-comments-plugin&app_key=sfYZJtStqjcANSKMpSN5VIaIUwwcBB6D&parent_limit=100'))
        self._test_item_results(results, 23)

    def test_parse_threads(self):
        threads = list(self.spider.parse_threads(mock_response_from_file('tests/assets/yle_mock_threads.html', 'https://yle-fi-search.api.yle.fi/v1/search?app_id=hakuylefi_v2_prod&app_key=4c1422b466ee676e03c4ba9866c0921f&language=fi&limit=10&offset=0&query=peruna&type=article')))
        self.assertEqual(len(threads), 11)


    
    