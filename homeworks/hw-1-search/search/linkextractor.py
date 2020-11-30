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
    max_empty_attempts = 3

    @classmethod
    @abstractmethod
    def get_selector(cls):
        """
        Abstract method to be implemented in subclasses. Specific to search engine used.
        :return: CSS selector (string) to be used to extract links to search results, within Beautiful Soup
        """
        pass

    @classmethod
    @abstractmethod
    def get_link_extractor(cls, elem):
        """
        Abstract method to be implemented in subclasses. Specific to search engine used.
        :param elem: object in Beautiful Soup, representing html node
        :return: string, link url for the search result link
        """
        pass

    @classmethod
    @abstractmethod
    def get_link_text_extractor(cls, elem):
        """
        Abstract method to be implemented in subclasses. Specific to search engine used.
        :param elem: object in Beautiful Soup, representing html node
        :return: string, text for the search result link
        """
        pass

    @classmethod
    @abstractmethod
    def next_search_page_url_generator(cls, query):
        """
        Abstract method to be implemented in subclasses. Specific to search engine used.
        Takes a string search query. Returns a generator object,which produces urls needed
        to get more results
        :param query: query string
        :return: a generator of string urls to query search engine with search results page 1, 2, etc.
        """
        pass

    @classmethod
    def logger(cls):
        """
        A shortcut method
        :return:
        """
        return SearchLogger.get_logger()

    @classmethod
    def _extract_elements_from_response(cls, response_text):
        """
        Extracts elements from parsed contents of a web page, according to the CSS selector
        :param response_text: Text contents of the web page
        :return: a list of Beautiful Soup objects representing "DOM nodes"
        """
        soup = BeautifulSoup(response_text, "lxml")
        return soup.select(cls.get_selector())

    @classmethod
    def _get_links_info(cls, elems):
        """
        Internal method.
        :param elems: a list of Beautiful Soup objects representing "DOM nodes"
        :return: a generator of objects {"url":..., "text":...}
        """
        for elem in elems:
            linkinfo = {
                "url": cls.get_link_extractor(elem),
                "text": cls.get_link_text_extractor(elem),
            }
            if linkinfo and linkinfo["url"]:
                yield linkinfo

    @classmethod
    def get_links_info(cls, response_text):
        """
        Gets search links from HTTP response text
        :param response_text:  string, HTTP response text
        :return: a generator of objects {"url":..., "text":...}
        """
        return cls._get_links_info(cls._extract_elements_from_response(response_text))

    @classmethod
    @with_delay(
        lambda cls: randomize_delay(cls.delay_in_seconds_between_search_requests)
    )
    def search_pages_contents_generator(cls, query, postprocessor=None):
        """

        :param query: search query (string)
        :param postprocessor: A function to be applied to the HTTP response text
        :return: a generator of HTTP response text values (optionally wrapped in
        <postprocessor>), for search engine result pages # 1, 2, ...
        """
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
        """
        Main method to implement the core of the search algorithm.
        :param query: search query string
        :param limit: Limit on a number of results
        :param depth_limit: recursion depth limit
        :param search_mode: string, can be 'all' or 'any'. Whether to require all query words
        to be contained in a link or description, or any of the query words
        :return: a generator of results
        """

        visited = set()         # Уже посещенные ссылки будут храниться тут

        query_words = QueryStopWords.remove_stop_words( # Расщепляем ссылку на слова, удаляем stop words
            [s for s in query.lower().split(" ") if s]
        )

        cls.logger().info(f"Final query words: {query_words}")

        # Генератор строк содержимого страниц поиска № 1, 2, ... для данного типа поисковика
        link_batch_gen = cls.search_pages_contents_generator(
            query, postprocessor=cls.get_links_info
        )

        def gen(parent_url, links, lev, search_page):
            """
            Основной рекурсивный генератор
            :param parent_url:  Родительская ссылка - для рекурсивного прохода, None для ссылок верхнего уровня.
            Параметр нужен для отчета и чтобы работать с относительными ссылками (превращать в абсолютные для
            дальнейшего прохода по ним)
            :param links:   Список объектов вида {"url":..., "text":...}. Это дочерние ссылки, по которым нужно
            будет пройти. В случае верхнего уровня, это будут результаты из поисковика, со страницы N (1, 2, ...) -
            в этом случае, parent_url = None. В случае рекурсии, это будут ссылки со страницы parent_url.
            :param lev: Текущая глубина рекурсии
            :param search_page: Номер страницы поиска. Нужен для отчета
            :return: генератор результатов - объектов вида
                {"url":..., "text":..., "rec.depth": lev, "parent_url":...}
            """
            newlinks = []  # Здесь будут храниться новые ссылки - т.е. те, по которым еще не проходили
            for link in links:
                link = fix_child_link(parent_url, link) # Восстанавливаем абсолютную ссылку
                canonical_url = to_canonical_url(link["url"]) # Приводим url к "каноническому" виду для хранения
                if canonical_url in visited:
                    # Уже были по этой ссылке - пропускаем
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
                        # Набрали достаточно результатов - выходим
                        return
            if lev == depth_limit - 1:
                # Cлишком большая глубина рекурсии - выходим
                return
            # Второй проход по новым ссылкам. Сами ссылки уже добавили, теперь будем
            # проходить рекурсивно по каждой. Это реализация поиска в ширину.
            for link in newlinks:
                if not link_is_valid_for_recursion(link):
                    # Ссылка определена как негодная для рекурсивного прохода - пропускаем
                    continue
                if lev > 0:
                    cls.logger().info(f"Recursing (level {lev}). About to read the url: {link['url']}")
                # Отправлеяем HTTP запрос по ссылке, получаем содержимое в виде строки
                link_contents = read_web_page(link["url"])
                if not link_contents:
                    # Что-то пошло не так с этой ссылкой. Пропускаем
                    cls.logger().warning("Could not read the page {}".format(link["url"]))
                    continue
                # Находим годные дочерние ссылки
                sublinks = [
                    link
                    for link in valid_page_links(
                        link_contents, query_words, mode=search_mode
                    )
                    if link_is_valid_for_recursion(link)
                ]

                # Рекурсивный вызов: перенаправляем генератор результатов от дочерних ссылок.
                yield from gen(link["url"], sublinks, lev + 1, search_page)

                # Небольшая случайная задержка между запросами - предосторожность на всякий случай
                time.sleep(
                    randomize_delay(cls.delay_in_seconds_between_normal_requests)
                )

        def full_gen(link_batch_generator):
            """
            Этот генератор соединяет рекурсивный проход, реализованный в gen(),
            с поставщиком списков ссылок от поисковика (<link_batch_generator>),
            и реализует полный генератор результатов. Таким образом, если рекурсивный
            проход не дал нужного количества результатов, мы автоматически запрашиваем
            следующую порцию результатов от поисковика, и вызываем gen() уже на них.
            В случае если параметр depth_limit=1, поиск вырождается в плоский
            (нерекурсивный) автоматически, так как gen() не будет вызывать себя
            снова.
            :param link_batch_generator: генератор списков ссылок от поисковика
            :return: генератор результатов - объектов вида
                {"url":..., "text":..., "rec.depth": lev, "parent_url":...}
            """
            empty_attempts = 0
            for index, links_batch in enumerate(link_batch_generator):
                # Получаем список ссылок от поисковика. index (+1) - это номер страницы результатов поиска
                links = list(links_batch)
                if not links:
                    empty_attempts += 1 # Пустой список ссылок может означать что мы наткнулись на защиту поисковика
                else:
                    empty_attempts = 0
                if empty_attempts >= cls.max_empty_attempts:
                    # Пустой список результатов несколько раз подряд. Похоже на защиту поисковика. Выходим.
                    cls.logger().warning(
                        f"Request to search engine returned an empty set of links for {empty_attempts} "+
                        "consecutive times. \nProbably hit captcha defence. You can try a different engine. "+
                        "Exiting..."
                    )
                    return
                # Вызываем (рекурсивный) проход по списку ссылок
                for link in gen(None, links, 0, index):
                    yield {**link, "search_page": index + 1}
                    if len(visited) == limit:
                        return

        def enumerated_gen(gen):
            """
            Добавляем индекс (порядковый номер) результата в объектам передаваемого генератора
            :param gen:
            :return:
            """
            for index, item in enumerate(gen):
                yield {**item, "index": index + 1}

        # Возвращаем окончательный генератор
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



