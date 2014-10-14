# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import os
## Third-party modules
import sqlite3
## NOC modules
from base import KVStorage

logger = logging.getLogger(__name__)


class SQLiteStorage(KVStorage):
    name = "sqlite"

    def __init__(self, database, partition):
        super(SQLiteStorage, self).__init__(database, partition)
        self.path = os.path.join("local", self.name,
                                 "%s.db" % self.partition)
        self.connection = sqlite3.connect(self.path)
        self.connection.isolation_level = None
        self.ensure_table()

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        cursor = self.connection.cursor()
        for k, v in batch:
            cursor.execute(
                "INSERT INTO ts(k, v) VALUES(?, ?)",
                [sqlite3.Binary(k), sqlite3.Binary(v)]
            )

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT k, v FROM ts WHERE k BETWEEN ? AND ? ORDER BY k",
            [sqlite3.Binary(start), sqlite3.Binary(end)]
        )
        for k, v in cursor.fetchall():
            yield k, v

    def ensure_table(self):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'ts'"
        )
        if cursor.fetchall()[0][0]:
            return
        logger.debug("Creating table ts")
        cursor.execute("CREATE TABLE ts(k BLOB, v BLOB)")
        cursor.execute("CREATE UNIQUE INDEX x_ts ON ts(k)")
