from tabulate import tabulate
import csv
import json
from .logger import SearchLogger


HEADERS_TRANSLATION = {
    'url': 'url',
    'text': 'Текст',
    'index': '№',
    'rec.depth': 'Глубина рекурсии',
    'parent_url': 'Родительская ссылка'
}

class ResultsHandler:

    @classmethod
    def get_headers(cls, verbose=False):
        if verbose:
            return ("index", "url", "text", "rec.depth", "parent_url")
        else:
            return ("index", "url", "text")

    @classmethod
    def _get_tabular_data(cls, search_data, headers):
        return {
            'headers': headers,
            'data': [[row[prop] for prop in headers] for row in search_data]
        }

    @classmethod
    def _console_print(cls, search_data, headers):
        print("\n\n*************                THE RESULTS                     *************\n\n")
        print(tabulate(
            cls._get_tabular_data(search_data, headers)["data"],
            headers=[HEADERS_TRANSLATION[h] for h in headers]
        ))

    @classmethod
    def console_print(cls, search_data,  verbose=False):
        headers = cls.get_headers(verbose=verbose)
        cls._console_print(search_data, headers)

    @classmethod
    def openwrite(cls, path):
        try:
            f = open(path, mode='w')
        except OSError:
            SearchLogger.get_logger().error(
                f"Error opening file {path} for writing. Search results could not be saved"
            )
            return None
        return f

    @classmethod
    def save_to_csv(cls, search_data, path, verbose=False):
        f = cls.openwrite(path)
        if not f:
            return
        headers = cls.get_headers(verbose=verbose)
        with f:
            writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(headers)
            for row in cls._get_tabular_data(search_data, headers)['data']:
                writer.writerow(row)
        SearchLogger.get_logger().info(f"Search results written to {path}")
        return True

    @classmethod
    def save_to_json(cls, search_data, path, verbose=False):
        f = cls.openwrite(path)
        if not f:
            return
        headers = cls.get_headers(verbose=verbose)
        filtered_data = [
            {key: row[key] for key in headers}
            for row in search_data
        ]
        with f:
            json.dump(filtered_data, f, indent=4)
        SearchLogger.get_logger().info(f"Search results written to {path}")
        return True

    @classmethod
    def save_results(cls, search_data, path, verbose=False):
        if not path:
            return None
        methods = {
            ".csv" : cls.save_to_csv,
            ".json": cls.save_to_json
        }
        for ext, method in methods.items():
            if path.endswith(ext):
                return method(search_data, path, verbose=verbose)
        return None

