from scrapy.http import Request, Response
import requests

import os

from scrapy.http import HtmlResponse

def mock_response_from_file(file_path, url, base_dir=None, meta=None):
    """
    Create a Scrapy fake HTTP response from a HTML file

    @param file_path: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    @param base_dir: The base directory to use for relative paths. Defaults to the current working directory.
    @param meta: Optional metadata to attach to the response request. Some
                 spiders read values from response.meta, so the response has
                 to be tied to a request that carries that metadata.

    returns: A scrapy HTTP response which can be used for unittesting.
    """

    if base_dir is None:
        base_dir = os.getcwd()

    file_path = os.path.join(base_dir, file_path)

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Were trying to open: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        body = f.read()

    request = Request(url, meta=meta) if meta is not None else None
    return HtmlResponse(url=url, body=body, encoding='utf-8', request=request)

def mock_response(url):
    """
    Create a mock HTTP response from a URL

    @param url: The URL of the response.

    returns: A scrapy HTTP response which can be used for unittesting.
    """
    request = Request(url)
    response = Response(url=url,
        request=request,
        body=requests.get(url).content)
    return response
