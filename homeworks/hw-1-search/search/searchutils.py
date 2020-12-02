import requests.exceptions
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import random
import time
from .logger import SearchLogger


def read_web_page(url):
    """
    Sends an HTTP request given the url, and returns the body of the response as a text (string), or None
    :param url: string url
    :return: string or None
    """
    headers = {
        "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
    except (requests.exceptions.RequestException, requests.ConnectionError):
        SearchLogger.get_logger().warning(f"Error reading the url: {url}. \n")
        return None
    if response.status_code != 200:
        SearchLogger.get_logger().warning(
            f"Bad response from the server for url {url}. Response code: {response.status_code}"
        )
        return None
    return response.text


def link_is_valid(link_info, query_words, mode="all"):
    """
    Tests if a link is valid to keep in search results, for a given query
    :param link_info: a dict with keys "url" and "text"
    :param query_words: a list of query words
    :param mode: can be "all" (default), or "any"
    :return: True or False
    If <mode> is "all", will return True if all query words are be present in
    either url or text. If <mode> is "any", will return True if any of the query
    words are be present in either url or text.
    """
    if not link_info["url"].startswith("http"):
        return False
    if mode == "all":
        combiner = all
    elif mode == "any":
        combiner = any
    else:
        combiner = all

    result = combiner(
        [
            word in link_info["url"] or link_info["text"] and word in link_info["text"].lower()
            for word in query_words
        ]
    )
    return result


def link_is_valid_for_recursion(link_info):
    """
    Make sure we don't try to read files like .pdf, etc
    :param link_info:
    :return: True or False
    """
    # TODO: improve this check to make it more robust
    if link_info["url"].endswith(".pdf") or link_info["url"].endswith(".zip"):
        return False
    return True


def to_canonical_url(url):
    """
    Converts a url into a "canonical" form, suitable for hashing. Keeps only scheme,
    domain and path. Ignores url query, fragment, and all other parts of the url.
    :param url: a string
    :return: a string
    """
    parsed_url = urlparse(url)
    return urlunparse([
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        '',
        '',
        ''
    ])


def page_links(page_contents):
    """
    Collects links from parsed web page
    :param page_contents: text (string)
    :return: a list of dicts with keys 'url' and 'text'
    """
    soup = BeautifulSoup(page_contents, 'lxml')
    return [
        {
            'url': to_canonical_url(link_elem.get("href")),
            'text': link_elem.getText()
        } for link_elem in soup.select("a")
    ]


def valid_page_links(page_contents, query_words, mode="all"):
    """
    Collect valid links from a web page
    :param page_contents: string, web page contents as text
    :param query_words: a list of query words (strings). Assumed to be in lower case
    :param mode: "any" or "all"
    :return: filtered list of objects {'url':..., 'text':...}, which are considered
    valid as search results.
    """
    return [
        linfo
        for linfo in page_links(page_contents)
        if type(linfo["url"]) == str and link_is_valid(linfo, query_words, mode=mode)
    ]


def fix_child_link(parent_url, link):
    """
    Form a valid absolute link for a relative link
    :param parent_url: string or None
    :param link: string url (can be relative)
    :return: string, absolute url
    """
    if link["url"].startswith("/") and parent_url:
        print("Parent_url: ", parent_url)
        if parent_url.endswith("/"):
            return {**link, "url": f"{parent_url[:-1]}{link['url']}"}
        else:
            return {**link, "url": f"{parent_url}{link['url']}"}
    else:
        return link


def randomize_delay(delay):
    """
    Compute a random delay value from a fixed base value
    :param delay: numeric positive, base delay value
    :return: random value that is guaranteed to be between <delay> and 2 * <delay>
    """
    return delay * (1 + random.randrange(10) / 10)


def with_delay(delay_func):
    """
    A decorator for class methods which return generators. Add delays in between
    calls to yield in a generator, based on a delay function
    :param delay_func: a function which takes class as a parameter and returns delay value
    :return: generator wrapper
    """
    def inner(generator):
        def generator_wrapper(cls, *args, **kwargs):
            for item in generator(cls, *args, **kwargs):
                next_delay = delay_func(cls)
                start = time.time()
                yield item
                end = time.time()
                time_left = next_delay - (end - start)
                if time_left > 0:
                    SearchLogger.get_logger().info(f"Going to sleep for {time_left} seconds...")
                    time.sleep(time_left)
        return generator_wrapper
    return inner
