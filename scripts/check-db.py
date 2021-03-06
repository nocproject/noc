#!./bin/python
# ----------------------------------------------------------------------
# Check database connection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import sys


def check_pg():
    import psycopg2
    from django.db import connection

    try:
        connection.cursor()
    except psycopg2.OperationalError as why:
        sys.stderr.write("ERROR: %s\n" % why)
        sys.exit(1)


def check_mongo():
    from noc.core.mongo.connection import get_db
    import pymongo

    try:
        db = get_db()
    except pymongo.errors.OperationFailure as why:
        sys.stderr.write("ERROR: %s\n" % why)
        sys.exit(1)
    version = db.connection.server_info()["version"]
    major, minor, rest = version.split(".", 2)
    major = int(major)
    minor = int(minor)
    if major < 2 or (major == 2 and minor < 4):
        sys.stderr.write("ERROR: MongoDB 2.4 or later required")
        sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1] == "--pg":
        check_pg()
    elif sys.argv[1] == "--mongo":
        check_mongo()
