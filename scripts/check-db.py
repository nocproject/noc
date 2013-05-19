#!./bin/python
##----------------------------------------------------------------------
## Check database connection
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##---------------------------------------------------------------------

import sys


def check_pg():
    import psycopg2
    from django.db import connection
    try:
        c = connection.cursor()
    except psycopg2.OperationalError, why:
        sys.stderr.write("ERROR: %s\n" % why)
        sys.exit(1)


def check_mongo():
    from noc.lib.nosql import get_db
    import pymongo
    try:
        db = get_db()
    except pymongo.errors.OperationFailure, why:
        sys.stderr.write("ERROR: %s\n" % why)
        sys.exit(1)


if __name__ == "__main__":
    if sys.argv[1] == "--pg":
        check_pg()
    elif sys.argv[1] == "--mongo":
        check_mongo()
