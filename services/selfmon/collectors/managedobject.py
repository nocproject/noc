# ----------------------------------------------------------------------
# ManagedObjectCollector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.main.models.pool import Pool
from noc.wf.models.state import State
from .base import BaseCollector


class ManagedObjectCollector(BaseCollector):
    name = "managedobject"

    SQL_POOL_MO = """SELECT
      pool AS pool_id,
      state AS state_id,
      COUNT(*) AS pool_state_count
    FROM sa_managedobject
    GROUP BY pool, state
    """

    def iter_metrics(self):
        pool_stat = defaultdict(int)
        for pool_id, state_id, count in self.pg_execute(self.SQL_POOL_MO):
            pool = Pool.get_by_id(pool_id)
            state = State.get_by_id(state_id)
            if not pool or not state:
                continue
            yield ("inventory_managedobject_count", ("pool", pool.name), ("state", state.name)), count
        for pool_name, count in pool_stat.items():
            yield ("inventory_managedobject_total", ("pool", pool_name)), count
