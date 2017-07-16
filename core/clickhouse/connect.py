# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Clickhouse connection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import urllib
# Third-party modules
import six
# NOC modules
from noc.core.http.client import fetch_sync
from noc.config import config


class ClickhouseError(Exception):
    pass


class ClickhouseClient(object):
    # @fixme took better one from config with shard settings
    HOST = os.environ.get("NOC_CLICKHOUSE_HOST", "clickhouse")
    PORT = os.environ.get("NOC_CLICKHOUSE_PORT", 8123)
    DB = config.clickhouse.db
    REQUEST_TIMEOUT = config.clickhouse.request_timeout
    CONNECT_TIMEOUT = config.clickhouse.connect_timeout

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
        code, headers, body = fetch_sync(
            url,
            method="POST" if post else "GET",
            body=post if post else None,
            connect_timeout=self.CONNECT_TIMEOUT,
            request_timeout=self.REQUEST_TIMEOUT
        )
        if code != 200:
            raise ClickhouseError("%s: %s" % (code, body))
        return [
            row.split("\t") for row in body.splitlines()
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
