# ----------------------------------------------------------------------
# ORACLE Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from threading import Condition

# NOC modules
from noc.core.threadpool import ThreadPoolExecutor
from .sql import SQLExtractor


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
        super().__init__(*args, **kwargs)
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
                    sid=self.config.get("ORACLE_SID"),
                )
            user = self.config.get("ORACLE_USER")
            password = self.config.get("ORACLE_PASSWORD")
            if user and password:
                self.connect = cx_Oracle.connect(
                    user=user, password=password, dsn=dsn, threaded=is_threaded
                )
            else:
                self.connect = cx_Oracle.connect(dsn, threaded=is_threaded)
            os.environ = old_env  # Restore environment
        cursor = self.connect.cursor()
        if self.config.get("ORACLE_ARRAYSIZE"):
            cursor.arraysize = int(self.config["ORACLE_ARRAYSIZE"])
        return cursor

    def iter_data_single(self):
        cursor = self.get_cursor()
        # Fetch data
        self.logger.info("Fetching data")
        for query, params in self.get_sql():
            cursor.execute(query, params)
            yield from cursor

    def iter_data_parallel(self, concurrency):
        def fetch_sql(query, params):
            cursor = self.get_cursor()
            cursor.execute(query, params)
            out = list(cursor)
            with cond:
                buffer.append(out)
                cond.notify()

        cond = Condition()
        buffer = []
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            left = 0
            for query, params in self.get_sql():
                left += 1
                pool.submit(fetch_sql, query, params)
            while left > 0:
                with cond:
                    if not buffer:
                        cond.wait()
                    data, buffer = buffer, []
                for seq in data:
                    yield from seq
                    left -= 1

    def iter_data(self, checkpoint=None, **kwargs):
        concurrency = int(self.config.get("ORACLE_ARRAYSIZE", 1))
        if concurrency == 1:
            yield from self.iter_data_single()
        else:
            yield from self.iter_data_parallel(concurrency)
