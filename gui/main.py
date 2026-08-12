# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Signal, Slot, QUrl

import pkgutil
import inspect
import threading
import importlib

import uh_scrapy.spiders as spiders_pkg
from scrapy import Spider

# `resources` lives in the gui package. Use a fallback so the app can run as a
# script (gui/ on sys.path), as a module (python -m gui.main), or frozen.
try:
    from resources import resource_path
except ImportError:
    from .resources import resource_path

# Explicit list of the spider modules that ship with the application. Declared
# here (and as PyInstaller hidden imports) because pkgutil.iter_modules cannot
# discover dynamically imported modules inside a frozen executable.
SPIDER_MODULES = [
    "kauppalehti_spider",
    "test_spider",
    "yle_spider",
    "hevostalli_spider",
    "hs_spider",
    "vauva_spider",
    "kaksplus_spider",
]

def load_spider_classes():
    spider_classes = {}

    # When frozen, iterate the known module names; otherwise auto-discover.
    if getattr(sys, "frozen", False):
        module_names = SPIDER_MODULES
    else:
        module_names = [m.name for m in pkgutil.iter_modules(spiders_pkg.__path__)]

    for module_name in module_names:
        full_name = f"{spiders_pkg.__name__}.{module_name}"

        # Dynamically import module
        module = importlib.import_module(full_name)

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

        try:
            from run_collection import run_spiders
        except ImportError:
            from .run_collection import run_spiders

        spider_names = [spiders[forum].name for forum in forums]

        def run():
            try:
                run_spiders(spider_names, search, startDate, endDate, file)
            finally:
                self._process = None
                self.collectionFinished.emit()

        try:
            self._process = threading.Thread(target=run, daemon=True)
            self._process.start()
        except Exception as e:
            print("Failed to start collection:", e)
            self._process = None
            return

        self.collectionStarted.emit()

if __name__ == "__main__":

    

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    backend = Backend()

    engine.rootContext().setContextProperty("spiders", list(spiders.keys()) )
    engine.rootContext().setContextProperty("backend", backend)

    qml_file = resource_path("main.qml")
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
