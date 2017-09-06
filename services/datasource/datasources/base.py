# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseDatasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.main.models.datasourcecache import DataSourceCache
from noc.config import config


class BaseDataSource(object):
    name = None
    CACHE_COLLECTION = "datasource_caches"
    lock = None
    ttl = config.datasource.default_ttl

    def get(self):
        try:
            if self.lock:
                self.lock.acquire()
            # Try to get cached data
            data = DataSourceCache.get_data(self.name)
            if not data:
                data = self.extract()
                DataSourceCache.set_data(self.name, data, self.ttl)
            return data
        finally:
            if self.lock:
                self.lock.release()

    def extract(self):
        """
        Generate list of rows. Each row is a list of fields
        :return:
        """
        raise NotImplementedError
