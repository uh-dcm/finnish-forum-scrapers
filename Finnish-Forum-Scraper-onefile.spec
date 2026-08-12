# -*- mode: python ; coding: utf-8 -*-
# PyInstaller ONE-FILE spec for Finnish Forum Scraper GUI.
#
# Build with:
#     pyinstaller --noconfirm --clean Finnish-Forum-Scraper-onefile.spec
#
# Produces a single self-contained executable:
#     dist/FinnishForumScraper.exe
#
# Note: PySide6/QML apps are large and onefile builds start more slowly than
# the onedir build (Finnish-Forum-Scraper.spec), but this produces a single
# distributable .exe.

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

# --- Bundle every PySide6 Qt module/plugin/QML we might need. ---------------
pyside_datas, pyside_binaries, pyside_hidden = collect_all('PySide6')

# Scrapy's startup log reports versions with importlib.metadata.version(), so
# the distribution metadata (.dist-info) for those packages must be bundled.
metadata_datas = (
    copy_metadata('scrapy')
    + copy_metadata('lxml')
    + copy_metadata('cssselect')
    + copy_metadata('parsel')
    + copy_metadata('w3lib')
    + copy_metadata('Twisted')
    + copy_metadata('pyOpenSSL')
    + copy_metadata('cryptography')
)

# --- Scrapy pulls in a lot of dynamically imported dependencies. ------------
scrapy_datas, scrapy_binaries, scrapy_hidden = collect_all('scrapy')

# Scrapy/Twisted stack loads many modules at runtime via entry points/plugins.
heavy_deps = [
    'twisted', 'automat', 'hyperlink', 'incremental', 'zope',
    'service_identity', 'idna', 'parsel', 'w3lib', 'tldextract',
    'itemadapter', 'itemloaders', 'cssselect', 'defusedxml', 'requests',
    'certifi', 'filelock', 'protego',
]
heavy_hidden = []
for mod in heavy_deps:
    try:
        heavy_hidden += collect_submodules(mod)
    except Exception:
        pass
heavy_datas, heavy_binaries = [], []
for mod in ('tldextract', 'certifi', 'idna'):
    try:
        d, b, _ = collect_all(mod)
        heavy_datas += d
        heavy_binaries += b
    except Exception:
        pass

# Explicitly hook in every spider shipped with the app. Name each module
# directly rather than relying on collect_submodules, which can silently return
# nothing if importing the package fails during analysis.
spider_hidden = [
    'uh_scrapy.spiders',
    'uh_scrapy.spiders.hevostalli_spider',
    'uh_scrapy.spiders.hs_spider',
    'uh_scrapy.spiders.kaksplus_spider',
    'uh_scrapy.spiders.kauppalehti_spider',
    'uh_scrapy.spiders.test_spider',
    'uh_scrapy.spiders.vauva_spider',
    'uh_scrapy.spiders.yle_spider',
]

hiddenimports = (
    pyside_hidden
    + scrapy_hidden
    + heavy_hidden
    + spider_hidden
    + [
        'uh_scrapy.pipelines',
        'uh_scrapy.middlewares',
        'uh_scrapy.items',
        'resources',
        'run_collection',
    ]
)

datas = pyside_datas + scrapy_datas + heavy_datas + metadata_datas
binaries = pyside_binaries + scrapy_binaries + heavy_binaries

# --- Bundle the QML files next to the entry point.---------------------------
datas += [
    ('gui/main.qml', '.'),
    ('gui/DateCalendar.qml', '.'),
    ('config.ini', '.'),
    ('constants.py', '.'),
]

a = Analysis(
    ['gui/main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hooks/rthook-scrapy-main.py'],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FinnishForumScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
