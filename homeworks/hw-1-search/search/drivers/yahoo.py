import re
import urllib
from search.linkextractor import SEDriverRegistry, AbstractLinkExtractor

class YahooLinkExtractor(AbstractLinkExtractor):

    @classmethod
    def get_selector(cls):
        return "div.algo.algo-sr > div > h3 > a"

    @classmethod
    def get_link_extractor(cls, elem):
        full_link = elem.get("href")
        inner_links = re.findall("https?%3a.*/RK", full_link)
        if not inner_links:
            return None
        encoded = inner_links[0][:-3]
        return re.sub("%2f", "/", re.sub("%3a", ":", encoded))

    @classmethod
    def get_link_text_extractor(cls, elem):
        return elem.getText()

    @classmethod
    def next_search_page_url_generator(cls, query):
        start = 0
        query = urllib.parse.quote(query)
        while True:
            url = "https://search.yahoo.com/search?p={}&fr=yfp-t&ei=UTF-8&fp=1".format(query)
            if start:
                url += "&b={}".format(start * 10 + 1)
            start += 1
            yield url

SEDriverRegistry.register("yahoo", YahooLinkExtractor)