from os import listdir
from os.path import isfile, join, dirname, splitext
import importlib

# This code loads the search engine drivers
drivers_dir = dirname(__file__)
drivers = [f for f in listdir(drivers_dir) if isfile(join(drivers_dir, f)) and f != "__init__.py"]
for f in drivers:
    importlib.import_module(f"search.drivers.{splitext(f)[0]}")
