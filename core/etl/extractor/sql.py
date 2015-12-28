# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SQL Data Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from base import BaseExtractor


class SQLExtractor(BaseExtractor):
    SQL = "SELECT 1"

    def get_sql(self):
        """
        Returns tuple of SQL Query, list of bind parameters
        """
        return self.SQL, []
