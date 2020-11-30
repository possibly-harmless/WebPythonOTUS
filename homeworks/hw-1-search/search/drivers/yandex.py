import re
import urllib
from search.linkextractor import AbstractLinkExtractor, SEDriverRegistry

def memoize(func):
    memcache = {}

    def inner(*args):
        if args not in memcache:
            memcache[args] = func(*args)
        return memcache[args]

    return inner

@memoize
def get_yandex_adlink_pattern():
    return re.compile("^http://yabs.yandex.ru/.*")

class YandexLinkExtractor(AbstractLinkExtractor):

    # Yandex seems to be more sensitive to this
    delay_in_seconds_between_search_requests = 10

    @classmethod
    def get_selector(cls):
        return ".serp-item > div > h2 > a"

    @classmethod
    def get_link_extractor(cls, elem):
        url = elem.get("href")
        if get_yandex_adlink_pattern().match(url):
            url = None  # Excluding ads
        return url

    @classmethod
    def get_link_text_extractor(cls, elem):
        return elem.select(".organic__url-text")[0].getText()

    @classmethod
    def next_search_page_url_generator(cls, query):
        page = 0
        query = urllib.parse.quote(query)
        while True:
            url = "https://yandex.ru/search/?lr=2&text={}".format(query)
            if page:
                url += "&p={}".format(page)
            page += 1
            yield url

SEDriverRegistry.register("yandex", YandexLinkExtractor)