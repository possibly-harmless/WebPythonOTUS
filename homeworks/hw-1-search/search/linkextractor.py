from abc import ABC, abstractmethod
from .searchutils import *
from .stopwords import QueryStopWords
from .logger import SearchLogger


class AbstractLinkExtractor(ABC):
    """
    An abstract base class implementing the search algorithm. Drivers for specific
    search engines should inherit from this class and implement class methods:

    get_selector()
    get_link_extractor()
    get_link_text_extractor()
    next_search_page_url_generator()
    """
    delay_in_seconds_between_search_requests = 3
    delay_in_seconds_between_normal_requests = 0.5

    @classmethod
    @abstractmethod
    def get_selector(cls):
        pass

    @classmethod
    @abstractmethod
    def get_link_extractor(cls, elem):
        pass

    @classmethod
    @abstractmethod
    def get_link_text_extractor(cls, elem):
        pass

    @classmethod
    @abstractmethod
    def next_search_page_url_generator(cls, query):
        """
        Takes a string search query. Returns a generator object,
        which produces urls needed to get more results
        """
        pass

    @classmethod
    def logger(cls):
        return SearchLogger.get_logger()

    @classmethod
    def _extract_elements_from_response(cls, response_text):
        soup = BeautifulSoup(response_text, "lxml")
        return soup.select(cls.get_selector())

    @classmethod
    def _get_links_info(cls, elems):
        for elem in elems:
            linkinfo = {
                "url": cls.get_link_extractor(elem),
                "text": cls.get_link_text_extractor(elem),
            }
            if linkinfo and linkinfo["url"]:
                yield linkinfo

    @classmethod
    def get_links_info(cls, response_text):
        return cls._get_links_info(cls._extract_elements_from_response(response_text))

    @classmethod
    @with_delay(
        lambda cls: randomize_delay(cls.delay_in_seconds_between_search_requests)
    )
    def search_pages_contents_generator(cls, query, postprocessor=None):
        for next_search_results_page_url in cls.next_search_page_url_generator(query):
            cls.logger().info(
                "About to query the search engine, url: {}".format(
                    next_search_results_page_url
                )
            )
            response_text = read_web_page(next_search_results_page_url)
            if not response_text:
                cls.logger().warning(
                    f"Unable to read url: {next_search_results_page_url}. Proceeding to the next url..."
                )
                break
            yield response_text if not postprocessor else postprocessor(response_text)

    @classmethod
    def recursive_link_generator(
            cls, query, limit=100, depth_limit=5, search_mode="all"
    ):
        visited = set()
        query_words = QueryStopWords.remove_stop_words([s for s in query.lower().split(" ") if s])

        cls.logger().info(f"Final query words: {query_words}")

        link_batch_gen = cls.search_pages_contents_generator(
            query, postprocessor=cls.get_links_info
        )

        def gen(parent_url, links, lev, search_page):
            newlinks = []
            for link in links:
                link = fix_child_link(parent_url, link)
                canonical_url = to_canonical_url(link["url"])
                if canonical_url in visited:
                    continue
                else:
                    cls.logger().info(f"Adding link: {canonical_url}")
                    visited.add(canonical_url)
                    newlinks.append(link)
                    yield {
                        **link,
                        "rec.depth": lev,
                        "parent_url": parent_url
                    }
                    if len(visited) == limit:  # Note that len is O(1)
                        return
            if lev == depth_limit - 1:
                return
            for link in newlinks:
                if not link_is_valid_for_recursion(link):
                    continue
                if lev > 0:
                    cls.logger().info(f"Recursing (level {lev}). About to read the url: {link['url']}")
                link_contents = read_web_page(link["url"])
                if not link_contents:
                    cls.logger().warning("Could not read the page {}".format(link["url"]))
                    continue
                sublinks = [
                    link
                    for link in valid_page_links(
                        link_contents, query_words, mode=search_mode
                    )
                    if link_is_valid_for_recursion(link)
                ]

                yield from gen(link["url"], sublinks, lev + 1, search_page)

                time.sleep(
                    randomize_delay(cls.delay_in_seconds_between_normal_requests)
                )

        def full_gen(link_batch_generator):
            for index, links_batch in enumerate(link_batch_generator):
                links = list(links_batch)
                for link in gen(None, links, 0, index):
                    yield {**link, "search_page": index + 1}
                    if len(visited) == limit:
                        return

        def enumerated_gen(gen):
            for index, item in enumerate(gen):
                yield {**item, "index": index + 1}

        return enumerated_gen(full_gen(link_batch_gen))


class SEDriverRegistry:
    """
    A class to store registered search engine drivers. In principle, a simple dict
    could've been used, but this code could incorporate some extra future logic.
    """
    _registry = {}

    @classmethod
    def register(cls, name, driver_class):
        cls._registry[name] = driver_class

    @classmethod
    def get_driver(cls, name):
        return cls._registry.get(name, None)

    @classmethod
    def registered_drivers_names(cls):
        return cls._registry.keys()



