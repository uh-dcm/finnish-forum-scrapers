import sys
from pathlib import Path


def resource_path(relative: str) -> Path:
    """Resolve a path to a bundled resource both when running from source and
    when frozen with PyInstaller (one-file mode extracts files to _MEIPASS)."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative


def project_root() -> Path:
    """The directory that contains the uh_scrapy package."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent.parent
