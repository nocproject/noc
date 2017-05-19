# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ORACLE Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
# Third-party modules
from concurrent.futures import as_completed
# NOC modules
from sql import SQLExtractor
from noc.core.threadpool import ThreadPoolExecutor


class ORACLEExtractor(SQLExtractor):
    """
    Oracle SQL extractor.
    Requres cx_Oracle
    
    Configuration variables
    *ORACLE_DSN* - Oracle database DSN
    *ORACLE_HOST* - Oracle host (when *ORACLE_DSN* is empty)
    *ORACLE_PORT* - Oracle port (when *ORACLE_DSN* is empty)
    *ORACLE_SERVICE_NAME* - Oracle database service name (
      when *ORACLE_DSN* is empty)
    *ORACLE_SID* - Oracle database SID (when *ORACLE_DSN* is empty)
    *ORACLE_USER* - Oracle database user
    *ORACLE_PASSWORD* - Oracle database password
    
    *ORACLE_CONCURRENCY* - execute up to *ORACLE_CONCURRENCY* queries
      in parralel
    *ORACLE_ARRAYSIZE* - oracle client array size
    """
    def __init__(self, *args, **kwargs):
        super(ORACLEExtractor, self).__init__(*args, **kwargs)
        self.connect = None

    def get_cursor(self):
        import cx_Oracle

        if not self.connect:
            is_threaded = int(self.config.get("ORACLE_CONCURRENCY", 1)) > 1
            # Alter environment
            old_env = os.environ.copy()  # Save environment
            os.environ.update(self.system.config)
            # Connect to database
            self.logger.info("Connecting to database")
            dsn = self.config.get("ORACLE_DSN")
            if not dsn:
                dsn = cx_Oracle.makedsn(
                    host=self.config.get("ORACLE_HOST"),
                    port=self.config.get("ORACLE_PORT"),
                    service_name=self.config.get("ORACLE_SERVICE_NAME"),
                    sid=self.config.get("ORACLE_SID")
                )
            user = self.config.get("ORACLE_USER")
            password = self.config.get("ORACLE_PASSWORD"),
            if user and password:
                self.connect = cx_Oracle.connect(
                    user=user,
                    password=password,
                    dsn=dsn,
                    threaded=is_threaded
                )
            else:
                self.connect = cx_Oracle.connect(
                    dsn,
                    threaded=is_threaded
                )
            os.environ = old_env  # Restore environment
        cursor = self.connect.cursor()
        if self.config.get("ORACLE_ARRAYSIZE"):
            cursor.arraysize = int(self.config["ORACLE_ARRAYSIZE"])
        return cursor

    def iter_data(self):
        def fetch_sql(query, params):
            cursor = self.get_cursor()
            cursor.execute(query, params)
            return list(cursor)

        concurrency = int(self.config.get("ORACLE_ARRAYSIZE", 1))
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
