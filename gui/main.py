# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, QSettings, QUrl

import pkgutil
import inspect
import subprocess
import threading

import uh_scrapy.spiders as spiders_pkg
from scrapy import Spider

def load_spider_classes():
    spider_classes = {}

    # Iterate over all modules in the spiders/ directory
    for module_info in pkgutil.iter_modules(spiders_pkg.__path__):
        module_name = module_info.name
        full_name = f"{spiders_pkg.__name__}.{module_name}"

        # Dynamically import module
        module = __import__(full_name, fromlist=[''])

        # Extract classes defined in this module
        for name, obj in inspect.getmembers(module, inspect.isclass):

            # Only include classes that:
            # 1) Inherit from scrapy.Spider
            # 2) Are defined in this module (not imported)
            if issubclass(obj, Spider) and obj.__module__ == full_name:
                ## pick the name of the forum
                try:
                    name = obj.start_urls[0]
                    spider_classes[ name ] = obj
                except:
                    pass

    return spider_classes

spiders = load_spider_classes()

class Backend(QObject):
    collectionStarted = Signal()
    collectionFinished = Signal()

    def __init__(self):
        super().__init__()
        self._process = None

    @Slot('QVariantList',str,str,str, str)
    def on_spider_start(self, forums, search, startDate, endDate, file ):
        # Guard against starting a collection while another is already running.
        if self._process is not None or not forums:
            return

        script = Path(__file__).resolve().parent / "run_collection.py"
        cmd = [
            sys.executable,
            str(script),
            *(spiders[forum].name for forum in forums),
            "--query", search,
            "--timefrom", startDate,
            "--timeto", endDate,
            "--file", file,
        ]

        self._process = subprocess.Popen(cmd)
        self.collectionStarted.emit()

        def wait():
            self._process.wait()
            self._process = None
            self.collectionFinished.emit()

        threading.Thread(target=wait, daemon=True).start()

if __name__ == "__main__":

    

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = Backend()

    engine.rootContext().setContextProperty("spiders", list(spiders.keys()) )
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
