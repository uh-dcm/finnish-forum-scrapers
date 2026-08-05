# This Python file uses the following encoding: utf-8
import argparse
import sys
from pathlib import Path

# Make the project root importable regardless of the working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    parser = argparse.ArgumentParser(description="Run a forum data collection.")
    parser.add_argument("spiders", nargs="+", help="Scrapy spider names to run")
    parser.add_argument("--query", required=True)
    parser.add_argument("--timefrom", required=True)
    parser.add_argument("--timeto", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    settings = get_project_settings()
    settings.update({
        'QUERY': args.query,
        'TIMEFROM': args.timefrom,
        'TIMETO': args.timeto,
        'ITEM_PIPELINES': {
            'uh_scrapy.pipelines.TimestampFilterPipeline': 1,
            'uh_scrapy.pipelines.BodyFilterPipeline': 2,
        },
    })
    settings['FEEDS'] = {args.file: {'format': 'csv', 'overwrite': False}}

    process = CrawlerProcess(settings)
    for name in args.spiders:
        process.crawl(name)
    process.start(install_signal_handlers=False)


if __name__ == "__main__":
    main()
