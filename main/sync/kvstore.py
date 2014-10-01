# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Simple key-value store
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sqlite3
import logging
import os
## NOC modules
from noc.lib.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class KeyValueStore(object):
    TABLE = "kv"

    def __init__(self, path, indexes=None, fields=None):
        self.logger = PrefixLoggerAdapter(logger, path)
        self.path = path
        self.fields = ["uuid"] + list(fields or [])
        self.indexes = indexes or []
        self.connect = None

    def get_connect(self):
        if not self.connect:
            is_empty = not os.path.exists(self.path)
            self.logger.info("Connecting to database")
            self.connect = sqlite3.connect(self.path)
            self.logger.debug("SQLite version %s", sqlite3.version)
            if is_empty:
                self.logger.info("Formatting key-value store")
                c = self.connect.cursor()
                fields = ["%s TEXT" % f for f in self.fields]
                c.execute("CREATE TABLE %s(%s)" % (
                    self.TABLE, ",".join(fields)))
                for i in self.indexes:
                    self.logger.debug("Indexing %s", i)
                    c.execute("CREATE INDEX x_%s_%s ON %s(%s)" % (
                        self.TABLE, i, self.TABLE, i))
                self.connect.commit()
        return self.connect

    def commit(self):
        self.logger.debug("Commit")
        connect = self.get_connect()
        connect.commit()

    def cursor(self):
        connect = self.get_connect()
        return connect.cursor()

    def get(self, **kwargs):
        where = []
        args = []
        for k in kwargs:
            where += ["%s = ?" % k]
            args += [kwargs[k]]
        sql = "SELECT %s FROM %s WHERE %s" % (
            ", ".join(self.fields), self.TABLE, " AND ".join(where))
        self.logger.debug("%s %s", sql, args)
        c = self.cursor()
        c.execute(sql, tuple(args))
        r = c.fetchone()
        if not r:
            return None
        return dict(zip(self.fields, r))

    def find(self, **kwargs):
        where = []
        args = []
        for k in kwargs:
            where += ["%s = ?" % k]
            args += [kwargs[k]]
        sql = "SELECT %s FROM %s" % (", ".join(self.fields), self.TABLE)
        if where:
            sql += " WHERE %s" % " AND ".join(where)
        self.logger.debug("%s %s", sql, args)
        c = self.cursor()
        c.execute(sql, tuple(args))
        data = []
        for r in c.fetchall():
            data += [dict(zip(self.fields, r))]
        return data

    def put(self, uuid, **kwargs):
        self.logger.debug("PUT: uuid=%s, %s", uuid, kwargs)
        if self.get(uuid=uuid):
            sop = []
            args = []
            for k in kwargs:
                sop += ["%s = ?" % k]
                args += [kwargs[k]]
            args += [uuid]
            sql = "UPDATE %s SET %s WHERE uuid=?" % (
                self.TABLE, ", ".join(sop))
            self.logger.debug("%s %s", sql, args)
            c = self.cursor()
            c.execute(sql, tuple(args))
        else:
            sf = ["uuid"]
            args = [uuid]
            for k in kwargs:
                sf += [k]
                args += [kwargs[k]]
            c = self.cursor()
            c.execute("INSERT INTO %s(%s) VALUES(%s)" % (
                self.TABLE,
                ", ".join(sf),
                ", ".join(["?"] * (len(kwargs) + 1))
            ), tuple(args))
        self.commit()

    def delete(self, uuid):
        self.logger.debug("DELETE %s", uuid)
        sql = "DELETE FROM %s WHERE uuid=?" % self.TABLE
        self.logger.debug("%s %s", sql, (uuid,))
        c = self.cursor()
        c.execute(sql, (uuid,))
        self.commit()
