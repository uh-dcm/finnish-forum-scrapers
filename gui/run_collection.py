# This Python file uses the following encoding: utf-8
import argparse
import os
import sys
import threading

from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging, log_scrapy_info
from twisted.internet.defer import DeferredList

try:
    from resources import project_root
except ImportError:
    from .resources import project_root

# Multithreading is weird but is needed here.
# The reactor runs on the main thread and the spiders run on a background thread.
_reactor_lock = threading.Lock()
_reactor_thread = None
_reactor_ready = threading.Event()
_logging_configured = False


def _make_settings(query, timefrom, timeto, file, use_lemmatization=True):
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
    settings.set('USE_LEMMATIZATION', use_lemmatization)
    settings.set('ITEM_PIPELINES', {
        'uh_scrapy.pipelines.TimestampFilterPipeline': 1,
        'uh_scrapy.pipelines.BodyFilterPipeline': 2,
    })
    settings.set('FEEDS', {str(file): {'format': 'csv', 'overwrite': False}})
    return settings


def _ensure_reactor(settings):
    global _reactor_thread
    with _reactor_lock:
        if _reactor_thread is not None:
            return

        from scrapy.utils.reactor import install_reactor

        def bootstrap():
            global _logging_configured
            if not _logging_configured:
                configure_logging(settings)
                log_scrapy_info(settings)
                _logging_configured = True
            install_reactor(
                settings["TWISTED_REACTOR"], settings.get("ASYNCIO_EVENT_LOOP")
            )

            from twisted.internet import reactor
            _reactor_ready.set()
            reactor.run(installSignalHandlers=False)

        _reactor_thread = threading.Thread(target=bootstrap, daemon=True)
        _reactor_thread.start()
        _reactor_ready.wait()


def run_spiders(spider_names, query, timefrom, timeto, file, stop_event=None, use_lemmatization=True):
    # Spiders read 'config.ini' relative to the working directory and import
    # the bundled 'constants' module, so pivot to the bundle root first.
    root = project_root()
    try:
        os.chdir(str(root))
    except OSError:
        pass

    settings = _make_settings(query, timefrom, timeto, file, use_lemmatization)
    _ensure_reactor(settings)

    from twisted.internet import reactor

    runner = CrawlerRunner(settings)
    done = threading.Event()
    errors = []

    def on_crawls_done(result):
        for ok, res in result:
            if not ok:
                errors.append(res)
        done.set()

    def schedule():
        if stop_event is not None and stop_event.is_set():
            done.set()
            return
        deferreds = []
        for name in spider_names:
            deferreds.append(runner.crawl(name))
        DeferredList(deferreds, consumeErrors=True).addBoth(on_crawls_done)

    reactor.callFromThread(schedule)

    if stop_event is not None:
        def watch():
            stop_event.wait()
            reactor.callFromThread(
                lambda: runner.stop().addBoth(lambda _: done.set())
            )

        threading.Thread(target=watch, daemon=True).start()

    done.wait()
    if errors:
        raise errors[0].value


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