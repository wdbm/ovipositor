#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# convert_YOURLS_SQLite_database_to_ovipositor_database                        #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program converts a YOURLS SQLite database to an ovipositor database.    #
#                                                                              #
# copyright (C) 2017 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help                  display help message
    --version                   display version and exit

    --database_YOURLS=FILE      database [default: linkdb.db]
    --database_ovipositor=FILE  database [default: ovipositor.db]
"""

name        = "convert_YOURLS_SQLite_database_to_ovipositor_database"
__version__ = "2018-06-21T1656Z"

import datetime
import docopt
import inspect
import logging
import os
import subprocess
import sys
import time

import dataset
import shijian
import technicolor

log = logging.getLogger(name)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.DEBUG)

def main(options = docopt.docopt(__doc__)):
    if options["--version"]:
        print(__version__)
        exit()
    filename_database_YOURLS     = options["--database_YOURLS"]
    filename_database_ovipositor = options["--database_ovipositor"]
    if not os.path.isfile(filename_database_YOURLS):
        log.debug("database {filename} not found".format(filename = filename_database_YOURLS))
        sys.exit()
    database = access_database(filename = filename_database_YOURLS)
    name_table = "yourls_url"
    log.info("access table \"{name_table}\"".format(name_table = name_table))
    table = database[name_table]
    rows = []
    for index_row, row in enumerate(table):
        rows.append(
            dict(
                comment   = row["title"],
                count     = row["clicks"],
                IP        = row["ip"],
                shortlink = row["keyword"],
                timestamp = row["timestamp"],
                URL       = row["url"]
            )
        )
    ensure_database(filename = filename_database_ovipositor)
    database = access_database(filename = filename_database_ovipositor)
    name_table = "shortlinks"
    log.info("access table \"{name_table}\"".format(name_table = name_table))
    table = database[name_table]
    log.info("save retrieved data to table \"{name_table}\"".format(name_table = name_table))
    progress_extent = len(rows)
    progress = shijian.Progress()
    progress.engage_quick_calculation_mode()
    for index, row in enumerate(rows):
        table.insert(row)
        print(progress.add_datum(fraction = (index + 1) / float(progress_extent)))
    sys.exit()

def ensure_database(filename = "database.db"):
    if not os.path.isfile(filename):
        log.debug("database {filename} nonexistent; creating database".format(
            filename = filename
        ))
        create_database(filename = filename)

def create_database(filename = "database.db"):
    log.debug("create database {filename}".format(filename = filename))
    os.system("sqlite3 " + filename + " \"create table aTable(field1 int); drop table aTable;\"")

def access_database(filename = "database.db"):
    log.debug("access database {filename}".format(filename = filename))
    database = dataset.connect("sqlite:///" + filename)
    return database

if __name__ == "__main__":
    main()
