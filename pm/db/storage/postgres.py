# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MongoDB Key-Value storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.db import connection
## Third-party modules
import psycopg2
## NOC modules
from base import KVStorage

logger = logging.getLogger(__name__)


class PostgresStorage(KVStorage):
    name = "postgres"

    BATCH_SIZE = 10000

    def __init__(self, database, partition):
        super(PostgresStorage, self).__init__(database, partition)
        self.table = "ts_%s" % partition.replace(".", "_")
        self.ensure_table()

    def write(self, batch):
        """
        Batch save the data
        batch is a list of [(key, value), ...]
        """
        cursor = connection.cursor()
        while batch:
            values = [
                "(%s, %s)" % (
                    psycopg2.Binary(k),
                    psycopg2.Binary(v)
                ) for k, v in batch[:self.BATCH_SIZE]]
            sql = "INSERT INTO %s(k,v) VALUES %s" % (self.table, ",".join(values))
            batch = batch[self.BATCH_SIZE:]
            cursor.execute(sql)
            cursor.execute("COMMIT")

    def iterate(self, start, end):
        """
        Iterate all keys between k0 and k1
        """
        cursor = connection.cursor()
        cursor.execute(
            "SELECT k, v FROM %s WHERE k BETWEEN %%s AND %%s ORDER BY k" % self.table,
            [psycopg2.Binary(start), psycopg2.Binary(end)]
        )
        for k, v in cursor.fetchall():
            yield k, v

    def ensure_table(self):
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM pg_class WHERE relname = %s",
            [self.table]
        )
        if cursor.fetchall()[0][0]:
            return
        logger.debug("Creating table %s", self.table)
        cursor.execute("CREATE TABLE %s(k BYTEA NOT NULL PRIMARY KEY, v BYTEA)" % self.table)
        cursor.execute("COMMIT")
