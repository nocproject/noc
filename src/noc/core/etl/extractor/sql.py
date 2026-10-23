# ----------------------------------------------------------------------
# SQL Data Extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseExtractor


class SQLExtractor(BaseExtractor):
    SQL = "SELECT 1"

    def get_sql(self):
        """
        Returns tuple of SQL Query, list of bind parameters
        """
        if isinstance(self.SQL, list):
            for sql in self.SQL:
                yield sql, []
        else:
            yield self.SQL, []
