#!./bin/python
# ----------------------------------------------------------------------
# Write channel service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from time import perf_counter
from urllib.parse import quote as urllib_quote

# Third-party modules
from typing import List

# NOC modules
from noc.config import config


class Channel(object):
    def __init__(self, table: str, address: str, db: str):
        """
        :param table: ClickHouse table name
        :param address: ClickHouse address
        :param db: ClickHouse database

        :return:
        """
        self.name = table
        self.address = address
        self.db = db
        self.sql = "INSERT INTO %s FORMAT JSONEachRow" % table
        self.encoded_sql = urllib_quote(self.sql.encode("utf8"))
        self.n = 0
        self.data: List[bytes] = []
        self.last_updated = perf_counter()
        self.last_flushed = perf_counter()
        self.flushing = False
        self.url = "http://%s/?database=%s&query=%s" % (
            address,
            db,
            self.encoded_sql,
        )

    def feed(self, data: bytes):
        n = data.count(b"\n")
        if data[-1] != b"\n":
            n += 1
        self.n += n
        self.data += [data]
        return n

    def is_expired(self):
        if self.n:
            return False
        t = perf_counter()
        if self.data or self.flushing:
            return False
        return t - self.last_updated > config.chwriter.channel_expire_interval

    def is_ready(self):
        if not self.data or self.flushing:
            return False
        if self.n >= config.chwriter.batch_size:
            return True
        t = perf_counter()
        return (t - self.last_flushed) * 1000 >= config.chwriter.batch_delay_ms

    def get_data(self) -> bytes:
        self.n = 0
        data = b"\n".join(self.data)
        self.data = []
        return data

    def start_flushing(self):
        self.flushing = True

    def stop_flushing(self):
        self.flushing = False
        self.last_flushed = perf_counter()

    def get_insert_sql(self):
        return self.sql

    def get_encoded_insert_sql(self):
        return self.encoded_sql
