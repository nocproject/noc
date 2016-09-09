# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ORACLE Data Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
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
            self.connect = cx_Oracle.connect(self.config["dsn"])
            os.environ = old_env  # Restore environment
        cursor = self.connect.cursor()
        if self.config.get("arraysize"):
            cursor.arraysize = int(self.config["arraysize"])
        return cursor

    def iter_data(self):
        cursor = self.get_cursor()
        # Fetch data
        self.logger.info("Fetching data")
        for query, params in self.get_sql():
            cursor.execute(query, params)
            for row in cursor:
                yield row
