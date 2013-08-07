import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "gmail",
    version = "0.0.5",
    author = "Charlie Guo",
    author_email = "FIXME",
    description = ("A Pythonic interface for Google Mail."),
    license = "MIT",
    keywords = "google gmail",
    url = "https://github.com/charlierguo/gmail",
    packages=['gmail'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
    ],
)
