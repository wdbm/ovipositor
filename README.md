# ovipositor

Flask link-shortening service and database system

![](https://raw.githubusercontent.com/wdbm/ovipositor/master/media/ovipositor.png)

# credits

- name by Ellis Kay

# introduction

Ovipositor is a link-shortener web program. A long URL is entered, together with an optional shortlink and an optional comment. When creating a shortlink, the long URL and the shortlink are saved to a database. When an attempt is made to use a shortlink, the specified shortlink is searched for in the database and, if the shortlink is in the database, there is a redirect to its corresponding long URL.

![](https://raw.githubusercontent.com/wdbm/ovipositor/master/media/screenshot.png)

# setup

```Bash
sudo apt install sqlite
sudo pip install ovipositor
```

# usage

Ovipositor can be set running in a simple way:

```Bash
ovipositor
```

In case of hacking attempts, it can make some sense to have it restart regularly:

```Bash
while true; do
    ovipositor --restart_regularly
done
```

# ovipositor database structure

There is one table in an ovipositor database called "shortlinks". This table has 6 fields:

|**table field**|**description**                            |
|---------------|-------------------------------------------|
|comment        |shortlink descriptive comment              |
|count          |shortlink usage count                      |
|IP             |IP address that created the shortlink      |
|URL            |long URL to which the shortlink corresponds|
|shortlink      |shortlink text                             |
|timestamp      |shortlink creation timestamp               |

# examining databases

A database can be examined using [datavision](https://github.com/wdbm/datavision) [view_database_SQLite.py](https://github.com/wdbm/datavision/blob/master/view_database_SQLite.py).

# changing from YOURLS to ovipositor

An export dump should be made of the YOURLS MySQL database and the dump should be converted to an SQLite3 database. This can be done using [mysql2sqlite](https://github.com/dumblob/mysql2sqlite).

The YOURLS SQLite database then can be converted to an ovipositor database using the script `convert_YOURLS_SQLite_database_to_ovipositor_database.py`.

```Bash
convert_YOURLS_SQLite_database_to_ovipositor_database.py --help

convert_YOURLS_SQLite_database_to_ovipositor_database.py \
    --database_YOURLD=linkdb.db                          \
    --database_ovipositor=ovipositor.db
```

The YOURLS database contains three tables, "yourls_url", "sqlite_sequence" and "yourls_options". These tables have the following fields:

- yourls_url
    - clicks
    - ip
    - keyword
    - timestamp
    - title
    - url
- sqlite_sequence
    - name
    - seq
- yourls_options
    - option_id
    - option_name
    - option_value

In changing from YOURLS to ovipositor, the following database table and field conversions are made:

|**YOURLS**                     |**ovipositor**                 |
|-------------------------------|-------------------------------|
|yourls_url                     |shortlinks                     |
|clicks                         |count                          |
|ip                             |IP                             |
|keyword                        |shortlink                      |
|url                            |URL                            |
|timestamp (`datetime.datetime`)|timestamp (`datetime.datetime`)|
|title                          |comment                        |
