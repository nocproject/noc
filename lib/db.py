# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various database utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import subprocess
## Django modules
from django.utils import tree
from django.db.models import Q
from django.db import connection


class SQLExpression(object):
    def __init__(self, sql):
        self.sql = sql

    def as_sql(self, qn, connection):
        return "(%s)" % self.sql, []


class SQLNode(tree.Node):
    def __init__(self, sql):
        super(SQLNode, self).__init__()
        self.sql = sql

    def __deepcopy__(self, memodict):
        obj = super(SQLNode, self).__deepcopy__(memodict)
        obj.sql = self.sql
        return obj

    def add_to_query(self, query, aliases):
        query.where.add(SQLExpression(self.sql), self.connector)


def SQL(sql):
    """
    Q-style wrapper for SQL statement. Can be used in queryset
    together with Q
    """
    return Q(SQLNode(sql))


def check_postgis():
    """
    Check PostGIS is enabled on NOC's database
    :return: True if PostGIS enabled, False otherwise
    :rtype: bool
    """
    c = connection.cursor()
    c.execute("SELECT COUNT(*) FROM pg_class WHERE relname='geometry_columns'")
    return c.fetchall()[0][0] == 1


def check_srs():
    """
    Check spatial reference systems are loaded into database
    :return: True if spatial_ref_sys table is present and not-empty
    :rtype: bool
    """
    c = connection.cursor()
    c.execute("SELECT COUNT(*) FROM pg_class WHERE relname='spatial_ref_sys'")
    if c.fetchall()[0][0] == 0:
        return False
    c.execute("SELECT COUNT(*) FROM spatial_ref_sys")
    return c.fetchall()[0][0] > 0


def pg_sharedir():
    """
    Returns PostgreSQL share/ directory path or None
    :return:
    """
    try:
        p = subprocess.Popen(["pg_config", "--sharedir"],
                             stdout=subprocess.PIPE)
    except OSError:
        return None
    return p.stdout.read().strip()


def check_pg_superuser():
    """
    Check NOC's PostgreSQL user is superuser
    :return: True if superuser, False otherwise
    :rtype: bool
    """
    c = connection.cursor()
    c.execute("""
        SELECT COUNT(*)
        FROM pg_user
        WHERE usename = USER
            AND usesuper=true""")
    return c.fetchall()[0][0] == 1
