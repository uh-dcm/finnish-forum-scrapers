#!/usr/bin/env python3
"""Run the unit tests and print a clean per-site report."""

import io
import os
import sys
import xml.etree.ElementTree as ET
from contextlib import redirect_stderr, redirect_stdout

import pytest

SITE_NAMES = {
    "hevostalli": "forum.hevostalli.net",
    "hs": "hs.fi",
    "kaksplus": "keskustelu.kaksplus.fi",
    "kauppalehti": "keskustelu.kauppalehti.fi",
    "vauva": "vauva.fi",
    "yle": "yle.fi",
}

TEST_LABELS = {
    "test_scrape_thread": "Thread scraping",
    "test_parse_threads": "Thread list parsing",
    "test_parse_section": "Section parsing",
    "test_parse_threads_next_page": "Pagination parsing",
}


def _site_key(testcase):
    parts = testcase.get("classname", "").split(".")
    module = parts[-2] if len(parts) >= 2 else testcase.get("classname", "")
    if module.endswith("_spider_test"):
        return module[: -len("_spider_test")]
    return module


def _parse_results(xml_path):
    if not os.path.exists(xml_path):
        return None
    tree = ET.parse(xml_path)
    results = {}
    for testcase in tree.getroot().iter("testcase"):
        site = _site_key(testcase)
        name = testcase.get("name", "?")
        label = TEST_LABELS.get(name, name)
        passed = testcase.find("failure") is None and testcase.find("error") is None
        results.setdefault(site, []).append((label, passed))
    return results


def _print_report(results):
    print("=== Web Scraper Unit Tests ===")
    print()
    for site in sorted(results):
        print(f"Testing: {SITE_NAMES.get(site, site)}")
        for label, passed in results[site]:
            mark = "\u2713" if passed else "\u2717"
            print(f"  {mark} {label}")
        print()
    passed_sites = sum(1 for r in results.values() if all(p for _, p in r))
    print("=== Summary ===")
    print(f"Sites tested: {len(results)}")
    print(f"Passed: {passed_sites}")
    print(f"Failed: {len(results) - passed_sites}")


def main():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    xml_path = os.path.join(repo_root, "test-results.xml")

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exitcode = pytest.main([
                "--junitxml=" + xml_path,
                "-o", "addopts=",
                "-o", "log_cli=false",
                "-q",
                "-p", "no:cacheprovider",
            ])
    except SystemExit as exc:
        exitcode = exc.code if isinstance(exc.code, int) else 1

    results = _parse_results(xml_path)
    if results is None:
        print(stdout_buf.getvalue())
        print(stderr_buf.getvalue())
        print("Failed to produce test results (no JUnit XML was generated).")
        return 1

    _print_report(results)

    has_failures = any(not passed for results_list in results.values() for _, passed in results_list)
    if has_failures or not results:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())