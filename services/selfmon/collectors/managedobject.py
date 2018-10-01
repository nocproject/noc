# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObjectCollector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.main.models.pool import Pool
from .base import BaseCollector


class ManagedObjectCollector(BaseCollector):
    name = "managedobject"

    SQL_POOL_MO = """SELECT
      pool AS pool_id,
      COUNT(CASE WHEN is_managed THEN 1 END) AS pool_managed,
      COUNT(CASE WHEN NOT is_managed THEN 1 END) AS pool_unmanaged
    FROM sa_managedobject
    GROUP BY pool
    """

    def iter_metrics(self):
        for pool_id, pool_managed, pool_unmanaged in self.pg_execute(self.SQL_POOL_MO):
            pool = Pool.get_by_id(pool_id)
            if not pool:
                continue
            yield ("inventory_managedobject_managed", ("pool", pool.name)), pool_managed
            yield ("inventory_managedobject_unmanaged", ("pool", pool.name)), pool_unmanaged
            yield ("inventory_managedobject_total", ("pool", pool.name)), pool_managed + pool_unmanaged
