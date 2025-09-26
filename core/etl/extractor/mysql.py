# ----------------------------------------------------------------------
# Mysql Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# NOC modules
from noc.core.etl.extractor.sql import SQLExtractor


class MySQLExtractor(SQLExtractor):
    """
    Mysql SQL extractor.
    Requres pymysql

    Configuration variables
    *MYSQL_HOST* - Mysql host
    *MYSQL_PORT* - Mysql port
    *MYSQL_USER* - Mysql database user
    *MYSQL_PASSWORD* - Mysql database password
    *MYSQL_DB* - Mysql database
    *MYSQL_CHARSET* - Mysql charset
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connect = None

    def get_cursor(self):
        import pymysql

        if not self.connect:
            # Alter environment
            old_env = os.environ.copy()  # Save environment
            os.environ.update(self.system.config)
            # Connect to database
            self.logger.info("Connecting to database")
            self.connect = pymysql.connect(
                host=str(self.config.get("MYSQL_HOST")),
                port=int(self.config.get("MYSQL_PORT")),
                user=str(self.config.get("MYSQL_USER")),
                password=str(self.config.get("MYSQL_PASSWORD")),
                db=str(self.config.get("MYSQL_DB")),
                charset=str(
                    self.config.get("MYSQL_CHARSET")
                    if self.config.get("MYSQL_CHARSET")
                    else "utf8mb4"
                ),
            )

            os.environ = old_env  # Restore environment
        return self.connect.cursor()

    def iter_data(self, checkpoint=None, **kwargs):
        cursor = self.get_cursor()
        # Fetch data
        self.logger.info("Fetching data")
        for query, params in self.get_sql():
            cursor.execute(query, params)
            yield from cursor
