from os import listdir
from os.path import isfile, join, dirname, splitext


def parse_stopwords_file(filename):
    with open(filename) as f:
        content = f.readlines()
    return [w for w in [x.strip() for x in content] if w]


class QueryStopWords:
    _registry = None
    _stopwords_dir = dirname(__file__)

    @classmethod
    def _init_registry(cls):
        if cls._registry is not None:
            return
        files = [
            f
            for f in listdir(cls._stopwords_dir)
            if isfile(join(cls._stopwords_dir, f)) and f.endswith(".txt")
        ]
        cls._registry = {
            splitext(f)[0]: set(parse_stopwords_file(join(cls._stopwords_dir, f)))
            for f in files
        }

    @classmethod
    def remove_stop_words(cls, query_words):
        cls._init_registry()
        return [
            w
            for w in [word.lower() for word in query_words]
            if all([w not in stopwords for stopwords in cls._registry.values()])
        ]
