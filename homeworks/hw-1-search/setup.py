import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="lshifr-otus-websearch",
    version="1.0.0",
    description="Simple web search console interface based on one of several popular search engines. "
                "Homework #1 for OTUS WebPython 2020 course",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/possibly-harmless/WebPythonOTUS/tree/hw-1-search/homeworks/hw-1-search",
    author="Leonid Shifrin",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests", "beautifulsoup4", "lxml", "click", "tabulate"],
    entry_points={
        "console_scripts": [
            "websearch=search.__main__:main",
        ]
    },
)
