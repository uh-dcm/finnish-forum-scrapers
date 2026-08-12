# This Python file uses the following encoding: utf-8
import argparse
import os
import sys
import threading
import time

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

try:
    from resources import project_root
except ImportError:
    from .resources import project_root


def _make_settings(query, timefrom, timeto, file):
    # Load the project settings directly from the module instead of relying on
    # get_project_settings(), which reads scrapy.cfg from disk and is not
    # available inside a PyInstaller-frozen executable.
    sys.path.insert(0, str(project_root()))
    import uh_scrapy.settings as project_settings

    settings = Settings()
    settings.setmodule(project_settings, priority='project')

    settings.set('QUERY', query)
    settings.set('TIMEFROM', timefrom)
    settings.set('TIMETO', timeto)
    settings.set('ITEM_PIPELINES', {
        'uh_scrapy.pipelines.TimestampFilterPipeline': 1,
        'uh_scrapy.pipelines.BodyFilterPipeline': 2,
    })
    settings.set('FEEDS', {str(file): {'format': 'csv', 'overwrite': False}})
    return settings


def run_spiders(spider_names, query, timefrom, timeto, file, stop_event=None):
    # Spiders read 'config.ini' relative to the working directory and import
    # the bundled 'constants' module, so pivot to the bundle root first.
    root = project_root()
    try:
        os.chdir(str(root))
    except OSError:
        pass

    settings = _make_settings(query, timefrom, timeto, file)

    process = CrawlerProcess(settings)
    for name in spider_names:
        process.crawl(name)

    if stop_event is not None:
        # A watcher thread waits for the stop request and schedules
        # process.stop() on the Twisted reactor thread running the crawl.
        from twisted.internet import reactor

        def watch():
            stop_event.wait()
            # Retry until the reactor is up, to avoid racing with
            # process.start() starting the reactor.
            while True:
                try:
                    reactor.callFromThread(process.stop)
                except Exception:
                    time.sleep(0.1)
                    continue
                break

        threading.Thread(target=watch, daemon=True).start()

    process.start(install_signal_handlers=False)


def main():
    parser = argparse.ArgumentParser(description="Run a forum data collection.")
    parser.add_argument("spiders", nargs="+", help="Scrapy spider names to run")
    parser.add_argument("--query", required=True)
    parser.add_argument("--timefrom", required=True)
    parser.add_argument("--timeto", required=True)
    parser.add_argument("--file", required=True)
    args = parser.parse_args()

    run_spiders(args.spiders, args.query, args.timefrom, args.timeto, args.file)


if __name__ == "__main__":
    main()
