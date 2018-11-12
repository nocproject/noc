# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Clickhouse connection
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import urllib
import random
# Third-party modules
import six
# NOC modules
from noc.core.http.client import fetch_sync
from noc.config import config
from .error import ClickhouseError


class ClickhouseClient(object):
    def __init__(self, host=None, port=None, read_only=True):
        self.read_only = read_only
        if read_only:
            self.user = config.clickhouse.ro_user
            self.password = config.clickhouse.ro_password
        else:
            self.user = config.clickhouse.rw_user
            self.password = config.clickhouse.rw_password
        if host:
            self.addresses = ["%s:%s" % (host, port or 8123)]
        elif read_only:
            self.addresses = [str(x) for x in config.clickhouse.ro_addresses]
        else:
            self.addresses = [str(x) for x in config.clickhouse.rw_addresses]

    def execute(self, sql=None, args=None, nodb=False, post=None, extra=None):
        def q(v):
            # @todo: quote dates
            if isinstance(v, six.string_types):
                return "'%s'" % (v.replace("\\", "\\\\").replace("'", "\\'"))
            else:
                return str(v)

        qs = []
        if not nodb:
            qs += ["database=%s" % config.clickhouse.db]
        if extra:
            qs += ["%s=%s" % (k, v) for k, v in extra]
        if sql:
            if args:
                sql = sql % tuple(q(v) for v in args)
            if post:
                qs += ["query=%s" % urllib.quote(sql.encode('utf8'))]
            else:
                post = sql.encode('utf8')
        url = "http://%s/?%s" % (random.choice(self.addresses), "&".join(qs))
        code, headers, body = fetch_sync(
            url,
            method="POST",
            body=post,
            user=self.user,
            password=self.password,
            connect_timeout=config.clickhouse.connect_timeout,
            request_timeout=config.clickhouse.request_timeout
        )
        if code != 200:
            raise ClickhouseError("%s: %s" % (code, body))
        return [
            row.split("\t") for row in body.splitlines()
        ]

    def ensure_db(self):
        self.execute(
            post="CREATE DATABASE IF NOT EXISTS %s;" % config.clickhouse.db,
            nodb=True
        )

    def has_table(self, name):
        r = self.execute("""
            SELECT COUNT(*)
            FROM system.tables
            WHERE
              database=%s
              AND name = %s
        """, [config.clickhouse.db, name])
        return r and r[0][0] == "1"


def connection(host=None, port=None, read_only=True):
    return ClickhouseClient(host=host, port=port, read_only=read_only)
