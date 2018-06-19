#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

def main():
  setuptools.setup(
    name                 = "ovipositor",
    version              = "2018.06.19.2042",
    description          = "link-shortening website and database system",
    long_description     = long_description(),
    url                  = "https://github.com/wdbm/ovipositor",
    author               = "Will Breaden Madden",
    author_email         = "wbm@protonmail.ch",
    license              = "GPLv3",
    packages             = setuptools.find_packages(),
    install_requires     = [
                           "datetime",
                           "dataset",
                           "Flask",
                           "shijian",
                           "technicolor"
                           ],
    entry_points         = {
                           "ovipositor": ("ovipositor=ovipositor.__init__:main")
                           },
    scripts              = [
                           "convert_YOURLS_SQLite_database_to_ovipositor_database.py"
                           ],
    include_package_data = True,
    zip_safe             = False
  )

def long_description(filename = "README.md"):
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
