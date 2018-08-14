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
    -h, --help             display help message
    --version              display version and exit
    --database=FILENAME    database                                              [default: ovipositor.db]
    --home=TEXT            redirection URL for no shortlink entry or redirection [default: index.html]
    --redirect_HTTPS=BOOL  direct loaded HTTP URLS to HTTPS versions             [default: true]
    --logfile=FILENAME     log filename                                          [default: log.txt]
"""

import base64
import datetime
import docopt
import logging
import math
import os
import string
import sys
try:
  from urllib.parse import urlparse as urlparse
except:
  from urlparse import urlparse

import dataset
from flask import (
  Flask,
  make_response,
  redirect,
  render_template,
  request
)
import technicolor

name        = "ovipositor"
__version__ = "2018-08-14T1819Z"

log = logging.getLogger(name)
log.addHandler(technicolor.ColorisingStreamHandler())
log.setLevel(logging.DEBUG)

log.info(name + " " + __version__)

app = Flask(__name__)

def WSGI(argv=[]):
  global options
  options = docopt.docopt(__doc__, argv = argv)
  global filename_database
  global home_URL
  global redirect_HTTPS
  filename_database = options["--database"]
  home_URL          = options["--home"]
  filename_log      = options["--logfile"]
  redirect_HTTPS    = options["--redirect_HTTPS"].lower() == "true"
  ensure_database(filename = filename_database)
  return app

def main():
  global options
  options = docopt.docopt(__doc__)
  if options["--version"]:
    print(__version__)
    exit()
  global filename_database
  global home_URL
  global redirect_HTTPS
  filename_database = options["--database"]
  home_URL          = options["--home"]
  filename_log      = options["--logfile"]
  redirect_HTTPS    = options["--redirect_HTTPS"].lower() == "true"
  ensure_database(filename = filename_database)
  app.run(
    host     = "0.0.0.0",
    #port     = 80,
    port     = 443,
    debug    = False,
    threaded = True
  )
  sys.exit()

def ensure_database(filename = "database.db"):
  if not os.path.isfile(filename):
    log.info("database {filename} nonexistent; creating database".format(filename = filename))
    create_database(filename = filename)

def create_database(filename = "database.db"):
  log.info("create database {filename}".format(filename = filename))
  os.system("sqlite3 " + filename + " \"create table aTable(field1 int); drop table aTable;\"")

def access_database(filename = "database.db"):
  log.info("access database {filename}".format(filename = filename))
  database = dataset.connect("sqlite:///" + filename)
  return database

@app.route("/")
def index():
  log.info("route index")
  return redirect(home_URL)

@app.route("/robots.txt", methods = ["GET"])
def robots():
  try:
    response = make_response("User-agent: *\nDisallow: /")
    response.headers["Content-type"] = "text/plain"
    return response
  except:
    pass

@app.route("/ovipositor", methods = ["GET", "POST"])
def home():
  log.info("route home")
  try:
    if request.method == "POST":
      URL_long  = str(request.form.get("url"))
      shortlink = str(request.form.get("shortlink"))
      comment   = str(request.form.get("comment"))
      IP        = str(request.remote_addr)
      # If a shortlink is not specified, create one by base 64 encoding the specified URL.
      if shortlink == "":
        shortlink = base64.urlsafe_b64encode(URL_long)
      log.info("shorten URL {URL_long} to URL {shortlink} for {IP}".format(
        URL_long  = URL_long,
        shortlink = shortlink,
        IP        = IP
      ))
      # If a comment is not specified, set it to the URL.
      if not comment:
        comment = URL_long
      # Save the specified URL and the shortlink to database.
      # Access the database.
      database = access_database(filename = filename_database)
      table    = database["shortlinks"]
      # If the shortlink is specified in the database, update its entry while retaining its count,
      # IP, shortlink and timestamp information.
      result = table.find_one(shortlink = shortlink)
      if result is None:
        log.info("save shortlink to database")
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
        log.info("update shortlink in database")
        table.update(
          dict(
            id      = result["id"],
            comment = comment,
            URL     = URL_long,
          ),
          "id"
        )
      return render_template("home.html", message = "saved shortlink " + shortlink)
    return render_template("home.html")
  except:
    log.error("error")
    return render_template("home.html", message = "error")

@app.route("/<shortlink_received>")
def redirect_shortlink(shortlink_received):
  log.info("route redirect")
  try:
    if\
      shortlink_received != "index.html" and\
      shortlink_received != "favicon.ico":
      log.debug("look up shortlink {shortlink}".format(shortlink = shortlink_received))
      database = access_database(filename = filename_database)
      if "shortlinks" in database.tables:
        table = database["shortlinks"]
        result = table.find_one(shortlink = shortlink_received)
        if result is None:
          log.debug("shortlink not found")
          return render_template("home.html", message = "shortlink not found")
        else:
          log.debug("shortlink found, updating usage count")
          table.update(
            dict(
              id    = result["id"],
              count = result["count"] + 1,
            ),
            "id"
          )
          URL_long = result["URL"]
          if redirect_HTTPS:
            if URL_long.startswith("http://"):
                URL_long = URL_long.replace("http://", "https://")
                log.debug("change shortlink found from HTTP to HTTPS")
      log.debug("redirect to URL {URL_long}".format(URL_long = URL_long))
    else:
      URL_long = home_URL
    return redirect(URL_long)
  except Exception:
    log.error("shortlink error")
    return render_template("home.html", message = "shortlink error")

if __name__ == "__main__":
  main()
