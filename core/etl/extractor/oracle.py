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
    def iter_data(self):
        import cx_Oracle

        # Alter session
        env = self.config.get("env", {}) or {}
        old_env = os.environ.copy()  # Save environment
        os.environ.update(env)
        # Connect to database
        self.logger.info("Connecting to database")
        connect = cx_Oracle.connect(self.config["dsn"])
        os.environ = old_env  # Restore environment
        cursor = connect.cursor()
        if self.config.get("arraysize"):
            cursor.arraysize = int(self.config["arraysize"])
        # Fetch data
        self.logger.info("Fetching data")
        query, params = self.get_sql()
        cursor.execute(query, params)
        for row in cursor:
            yield row
