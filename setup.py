#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import setuptools

def main():

    setuptools.setup(
        name             = "ovipositor",
        version          = "2017.02.05.0157",
        description      = "link-shortening website and database system",
        long_description = long_description(),
        url              = "https://github.com/wdbm/ovipositor",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        py_modules       = [
                           "ovipositor"
                           ],
        install_requires = [
                           "datetime",
                           "dataset",
                           "Flask",
                           "propyte",
                           "pyprel",
                           "shijian"
                           ],
        scripts          = [
                           "convert_YOURLS_SQLite_database_to_ovipositor_database.py"
                           ],
        entry_points     = """
            [console_scripts]
            ovipositor = ovipositor:ovipositor
        """
    )

def long_description(
    filename = "README.md"
    ):

    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
