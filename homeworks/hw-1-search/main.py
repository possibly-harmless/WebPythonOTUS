import search.drivers  # Need this to load / register drivers
import click
from search.linkextractor import SEDriverRegistry
from search.results import ResultsHandler
from search.logger import SearchLogger, DEFAULT_LOG_PATH


DEFAULT_MAX_RESULTS = 30
DEFAULT_MAX_RECURSION_DEPTH = 5
DEFAULT_CONSOLE_FLAG = True
DEFAULT_SEARCH_ENGINE = "google"
DEFAULT_SEARCH_MODE = "all"
DEFAULT_VERBOSE_FLAG = False
DEFAULT_LOG_LEVEL = 'info'
DEFAULT_RECURSIVE_MODE = True

REGISTERED_ENGINES = SEDriverRegistry.registered_drivers_names()
SUPPORTED_SEARCH_MODES = ('any', 'all')
SUPPORTED_LOG_LEVELS = SearchLogger.log_level_mappings().keys()

@click.command()
@click.argument("query")
@click.option(
    "--engine",
    default=DEFAULT_SEARCH_ENGINE,
    type=click.Choice(REGISTERED_ENGINES),
    help=f"Search engine type. Defaults to '{DEFAULT_SEARCH_ENGINE}'"
)
@click.option(
    "--limit",
    default=DEFAULT_MAX_RESULTS,
    help=f"Max number of results to return. Default is {DEFAULT_MAX_RESULTS}"
)
@click.option(
    "--recursive/--non-recursive",
    default=DEFAULT_RECURSIVE_MODE,
    help="Whether the search is recursive (default) or not"
)
@click.option(
    "--console/--no-console",
    default=DEFAULT_CONSOLE_FLAG,
    # is_flag=True,
    help="Whether to print results to console (default) or not"
)
@click.option(
    "--mode",
    default=DEFAULT_SEARCH_MODE,
    type=click.Choice(SUPPORTED_SEARCH_MODES),
    help="""Keep only links with all (default) or any of the words in the query"""
)
@click.option(
    "--depth_limit",
    default=DEFAULT_MAX_RECURSION_DEPTH,
    help="Recursion depth limit. Defaults to 5"
)
@click.option(
    "--resultpath",
    default=None,
    help="A path to .csv or .json file to save the results to. Defaults to None"
)
@click.option(
    "--verbose/--brief",
    default=DEFAULT_VERBOSE_FLAG,
    is_flag=True,
    help="""Whether or not (default) to keep extended search information in results."""
)
@click.option(
    "--logpath",
    default=DEFAULT_LOG_PATH,
    help=f"Path to log file. Defaults to {DEFAULT_LOG_PATH}"
)
@click.option(
    "--loglevel",
    default=DEFAULT_LOG_LEVEL,
    type=click.Choice(SUPPORTED_LOG_LEVELS),
    help="Sets the log level. Defaults to 'info'"
)
def search(query, engine, limit, recursive,  console, mode, depth_limit, resultpath, verbose, logpath, loglevel):

    SearchLogger.init_logger(path=logpath, log_to_console=True, level=loglevel)
    logger = SearchLogger.get_logger()

    extractor = SEDriverRegistry.get_driver(engine)

    if not recursive:
        depth_limit = 1

    results = list(extractor.recursive_link_generator(
        query,
        limit=limit,
        search_mode=mode,
        depth_limit=depth_limit
    ))

    logger.info("Finished search...")

    if console:
        ResultsHandler.console_print(results, verbose=verbose)

    if resultpath:
        ResultsHandler.save_results(results, resultpath, verbose=verbose)


if __name__ == "__main__":
    search()

