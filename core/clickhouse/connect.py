# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Clickhouse connection
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import urllib
## Third-party modules
import pycurl
import six


class ClickhouseError(Exception):
    pass


class ClickhouseClient(object):
    HOST = os.environ.get("NOC_CLICKHOUSE_HOST", "clickhouse")
    PORT = os.environ.get("NOC_CLICKHOUSE_PORT", 8123)
    DB = os.environ.get("NOC_CLICKHOUSE_DB", "noc")
    REQUEST_TIMEOUT = 3600
    CONNECT_TIMEOUT = 10

    def __init__(self):
        pass

    def execute(self, sql=None, args=None, nodb=False, post=None):
        def q(v):
            # @todo: quote dates
            if isinstance(v, six.string_types):
                return "'%s'" % (v.replace("\\", "\\\\").replace("'", "\\'"))
            else:
                return str(v)

        qs = []
        if not nodb:
            qs += ["database=%s" % self.DB]
        if sql:
            if args:
                sql = sql % tuple(q(v) for v in args)
            qs += ["query=%s" % urllib.quote(sql.encode('utf8'))]
        url = "http://%s:%s/?%s" % (self.HOST, self.PORT, "&".join(qs))
        buff = six.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        if post:
            c.setopt(c.POST, 1)
            c.setopt(c.POSTFIELDS, post)
        c.setopt(c.WRITEDATA, buff)
        c.setopt(c.NOPROXY, "*")
        c.setopt(c.TIMEOUT, self.REQUEST_TIMEOUT)
        c.setopt(c.CONNECTTIMEOUT, self.CONNECT_TIMEOUT)
        c.setopt(c.TCP_KEEPALIVE, 1)
        c.setopt(c.TCP_KEEPIDLE, 60)
        c.setopt(c.TCP_KEEPINTVL, 60)
        try:
            c.perform()
        except pycurl.error as e:
            raise ClickhouseError(str(e))
        finally:
            code = c.getinfo(c.RESPONSE_CODE)
            c.close()
        v = buff.getvalue()
        if code != 200:
            raise ClickhouseError(v)
        return [
            row.split("\t") for row in v.splitlines()
        ]

    def ensure_db(self):
        self.execute(
            post="CREATE DATABASE IF NOT EXISTS %s;" % self.DB,
            nodb=True
        )

    def has_table(self, name):
        r = self.execute("""
            SELECT COUNT(*)
            FROM system.tables
            WHERE
              database=%s
              AND name = %s
        """, [self.DB, name])
        return r and r[0][0] == "1"


def connection():
    return ClickhouseClient()
