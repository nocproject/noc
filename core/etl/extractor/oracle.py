# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ORACLE Data Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## Third-party modules
from concurrent.futures import ThreadPoolExecutor, as_completed
## NOC modules
from sql import SQLExtractor


class ORACLEExtractor(SQLExtractor):
    def __init__(self, *args, **kwargs):
        super(ORACLEExtractor, self).__init__(*args, **kwargs)
        self.connect = None

    def get_cursor(self):
        import cx_Oracle

        if not self.connect:
            # Alter session
            env = self.config.get("env", {}) or {}
            old_env = os.environ.copy()  # Save environment
            os.environ.update(env)
            # Connect to database
            self.logger.info("Connecting to database")
            dsn = self.config.get("dsn")
            if not dsn:
                dsn = cx_Oracle.makedsn(
                    host=self.config.get("host"),
                    port=self.config.get("port"),
                    service_name=self.config.get("service_name"),
                    sid=self.config.get("sid")
                )
            self.connect = cx_Oracle.connect(
                dsn,
                threaded=int(self.config.get("concurrency", 1)) > 1
            )
            os.environ = old_env  # Restore environment
        cursor = self.connect.cursor()
        if self.config.get("arraysize"):
            cursor.arraysize = int(self.config["arraysize"])
        return cursor

    def iter_data(self):
        def fetch_sql(query, params):
            cursor = self.get_cursor()
            cursor.execute(query, params)
            return list(cursor)

        concurrency = int(self.config.get("concurrency", 1))
        if concurrency == 1:
            cursor = self.get_cursor()
            # Fetch data
            self.logger.info("Fetching data")
            for query, params in self.get_sql():
                cursor.execute(query, params)
                for row in cursor:
                    yield row
        else:
            with ThreadPoolExecutor(max_workers=concurrency) as pool:
                futures = [pool.submit(fetch_sql, query, params)
                           for query, params in self.get_sql()]
                for f in as_completed(futures):
                    for row in f.result():
                        yield row
