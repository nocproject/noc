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
        self.ensure_table()

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        self.connection.executemany(
            "INSERT INTO ts(k, v) VALUES(?, ?)",
            ((sqlite3.Binary(k), sqlite3.Binary(v)) for k, v in batch)
        )
        self.connection.commit()

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
        for c, in self.connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE name = 'ts'"
        ):
            if c:
                return
        logger.debug("Enabling WAL")
        self.connection.execute("PRAGMA journal_mode=WAL")
        logger.debug("Creating table ts")
        self.connection.execute("CREATE TABLE ts(k BLOB, v BLOB)")
        self.connection.execute("CREATE UNIQUE INDEX x_ts ON ts(k)")
