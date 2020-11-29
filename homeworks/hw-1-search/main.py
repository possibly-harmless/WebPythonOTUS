import search.drivers  # Need this to load / register drivers
from search.linkextractor import SEDriverRegistry
from search.results import ResultsHandler
from search.logger import SearchLogger



if __name__ == "__main__":
    extractor = SEDriverRegistry.get_driver("google")
    logger = SearchLogger.get_logger()
    glgen = extractor.recursive_link_generator(
        "python generator",
        limit=30,
        search_mode="all",
        depth_limit=5
    )
    results = list(glgen)
    ResultsHandler.console_print(results, verbose=False)
    ResultsHandler.save_to_csv(
        results,
        path="/Users/archie/Temp/search_results.csv",
        verbose=False
    )
    ResultsHandler.save_to_json(
        results,
        path="/Users/archie/Temp/search_results.json",
        verbose=False
    )

