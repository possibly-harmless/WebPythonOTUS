from search.linkextractor import SEDriverRegistry, AbstractLinkExtractor
import re


class GoogleLinkExtractor(AbstractLinkExtractor):

    @classmethod
    def get_selector(cls):
        return ".rc > div > a"

    @classmethod
    def get_link_extractor(cls, elem):
        href = elem.get('href')
        return href

    @classmethod
    def get_link_text_extractor(cls, elem):
        h3 = elem.find('h3')
        return '' if h3 is None else h3.getText()  # h3.find('div').getText()

    @classmethod
    def next_search_page_url_generator(cls, query):
        skip = 0
        query = re.sub("\s+", "+", query)
        while True:
            url = "https://www.google.com/search?q={}".format(query)
            if skip:
                url += "&start={}".format(int(skip / 10) * 10)
            skip += 10
            yield url


SEDriverRegistry.register("google", GoogleLinkExtractor)
