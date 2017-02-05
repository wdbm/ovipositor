#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# ovipositor                                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is a link-shortening website and database system.               #
#                                                                              #
# copyright (C) 2017 William Breaden Madden, name by Ellis Kay                 #
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
    -h, --help               display help message
    --version                display version and exit
    -v, --verbose            verbose logging
    -s, --silent             silent
    -u, --username=USERNAME  username
    --database=FILENAME      database [default: ovipositor.db]
    --url=text               URL      [default: http://127.0.0.1]
    --socket=text            socket   [default: 5000]
"""

name    = "ovipositor"
version = "2017-02-05T0245Z"
logo    = None

import base64
import docopt
import math
import os
import string
import urlparse

import datetime
import dataset
from flask import (
    Flask,
    redirect,
    render_template,
    request
)
import propyte
import pyprel
import shijian

application = Flask(__name__)

def main(options):

    global program
    program = propyte.Program(
        options = options,
        name    = name,
        version = version,
        logo    = logo
    )
    global log
    from propyte import log

    global filename_database
    global URL
    global socket
    filename_database = options["--database"]
    URL               = options["--url"]
    socket            = options["--socket"]

    ensure_database(filename = filename_database)

    if program.verbose:
        print_database_shortlinks(
            filename = filename_database
        )

    global application

    application.run(
        host  = "0.0.0.0",
        debug = program.verbose
    )

    program.terminate()

def ensure_database(
    filename = "database.db"
    ):

    if not os.path.isfile(filename):
        log.debug("database {filename} nonexistent; creating database".format(
            filename = filename
        ))
        create_database(filename = filename)

def create_database(
    filename = "database.db"
    ):

    log.debug("create database {filename}".format(
        filename = filename
    ))
    os.system(
        "sqlite3 " + \
        filename   + \
        " \"create table aTable(field1 int); drop table aTable;\""
    )

def access_database(
    filename = "database.db"
    ):

    log.debug("access database {filename}".format(
        filename = filename
    ))
    database = dataset.connect("sqlite:///" + filename)

    return database

def print_database_shortlinks(
    filename = "database.db"
    ):

    database = access_database(filename = filename_database)
    print(
        pyprel.Table(
            contents = pyprel.table_dataset_database_table(
                table = database["shortlinks"]
            )
        )
    )

@application.route("/", methods = ["GET", "POST"])
def home():

    log.debug("route home")

    if request.method == "POST":
        URL_long  = str(request.form.get("url"))
        shortlink = str(request.form.get("shortlink"))
        comment   = str(request.form.get("comment"))
        IP        = str(request.remote_addr)
        ## If the scheme of the URL is not specified, assume that it is HTTP.
        #if urlparse.urlparse(URL_long).scheme == "":
        #    URL_long = "http://" + URL_long
        # If a shortlink is not specified, create one by base 64 encoding the
        # specified URL.
        if shortlink == "":
            shortlink = base64.urlsafe_b64encode(URL_long)
        log.debug("shorten URL {URL_long} to URL {shortlink}".format(
            URL_long  = URL_long,
            shortlink = shortlink
        ))
        # If a comment is not specified, set it to the URL.
        if not comment:
            comment = URL
        # Save the specified URL and the shortlink to database.
        # Access the database.
        database = access_database(filename = filename_database)
        table    = database["shortlinks"]
        # If the shortlink is specified in the database, update its entry while
        # retaining its count, IP, shortlink and timestamp information.
        result = table.find_one(shortlink = shortlink)
        if result is None:
            table.insert(
                dict(
                    comment   = comment,
                    count     = 0,
                    IP        = IP,
                    shortlink = shortlink,
                    timestamp = datetime.datetime.utcnow(),
                    URL       = URL_long,
                )
            )
        else:
            table.update(
                dict(
                    id        = result["id"],
                    comment   = comment,
                    #count     = 0,
                    #IP        = IP,
                    #shortlink = shortlink,
                    #timestamp = datetime.datetime.utcnow(),
                    URL       = URL_long,
                ),
                "id"
            )

    if program.verbose:
        print_database_shortlinks(
            filename = filename_database
        )

    return render_template("home.html")

@application.route("/<shortlink_received>")
def redirect_shortlink(
    shortlink_received
    ):

    log.debug("route redirect")

    if shortlink_received != "favicon.ico":
        log.debug("look up shortlink {shortlink}".format(
            shortlink = shortlink_received
        ))
        database = access_database(filename = filename_database)
        if "shortlinks" in database.tables:
            table = database["shortlinks"]
            result = table.find_one(shortlink = shortlink_received)
            if result is None:
                log.debug("shortlink not found")
                URL_long = URL + ":" + socket
            else:
                log.debug("shortlink found, updating usage count")
                URL_long = result["URL"]
                table.update(
                    dict(
                        id        = result["id"],
                        #comment   = comment,
                        count     = result["count"] + 1,
                        #IP        = IP,
                        #shortlink = shortlink,
                        #timestamp = datetime.datetime.utcnow(),
                        #URL       = URL_long,
                    ),
                    "id"
                )

        log.debug("redirect to URL {URL}".format(
            URL = URL
        ))
    else:
        URL_long = URL + ":" + socket

    return redirect(URL_long)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
