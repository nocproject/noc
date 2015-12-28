# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ORACLE Data Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from sql import SQLExtractor


class ORACLEExtractor(SQLExtractor):
    def iter_data(self):
        import cx_Oracle

        self.logger.info("Connecting to database")
        connect = cx_Oracle.connect(self.config["dsn"])
        self.logger.info("Fetching data")
        cursor = connect.cursor()
        query, params = self.get_sql()
        cursor.execute(query, params)
        for row in cursor:
            yield row
